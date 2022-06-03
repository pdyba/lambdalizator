from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

from lbz.aws_boto3 import Boto3Client
from lbz.events.api import BaseEvent, EventAPI


class MyTestEvent(BaseEvent):
    type = "MY_TEST_EVENT"


class TestBaseEvent:
    def test_base_event_creation_and_structure(self) -> None:
        event = {"x": 1}
        new_event = MyTestEvent(event)

        assert new_event.type == "MY_TEST_EVENT"
        assert new_event.raw_data == {"x": 1}
        assert new_event.data == '{"x": 1}'

    def test__eq__same(self) -> None:
        new_event_1 = MyTestEvent({"x": 1})
        new_event_2 = MyTestEvent({"x": 1})

        assert new_event_1 == new_event_2

    def test__eq__different_data(self) -> None:
        new_event_1 = MyTestEvent({"x": 1})
        new_event_2 = MyTestEvent({"x": 2})

        assert new_event_1 != new_event_2

    def test__eq__different_type_same_data(self) -> None:
        class MySecondTestEvent(BaseEvent):
            type = "MY_SECOND_TEST_EVENT"

        new_event_1 = MyTestEvent({"x": 1})
        new_event_2 = MySecondTestEvent({"x": 1})

        assert new_event_1 != new_event_2


class TestEventApi:
    def setup_method(self) -> None:
        # pylint: disable= attribute-defined-outside-init
        self.event_api = EventAPI()

    def teardown_method(self, _test_method: Callable) -> None:
        # pylint: disable= attribute-defined-outside-init
        self.event_api._del()  # type: ignore # pylint: disable=protected-access

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test___repr__(self) -> None:
        expected_repr = (
            "<EventAPI bus: million-dollar-lambda-event-bus Events: pending=0 sent=0 failed=0>"
        )
        assert str(self.event_api) == expected_repr
        self.event_api.register(MyTestEvent({"x": 1}))
        self.event_api.register(MyTestEvent({"x": 1}))
        expected_repr = (
            "<EventAPI bus: million-dollar-lambda-event-bus Events: pending=2 sent=0 failed=0>"
        )
        assert str(self.event_api) == expected_repr
        self.event_api.send()
        expected_repr = (
            "<EventAPI bus: million-dollar-lambda-event-bus Events: pending=0 sent=2 failed=0>"
        )
        assert str(self.event_api) == expected_repr

    @patch.object(Boto3Client, "eventbridge")
    def test_settters(self, mock_send: MagicMock) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        self.event_api.set_resources(["Yy", "ZZ"])
        self.event_api.set_source("orgin")
        self.event_api.set_bus_name("magic-bus")

        self.event_api.send()

        mock_send.put_events.assert_called_once_with(
            Entries=[
                {
                    "Detail": '{"x": 1}',
                    "DetailType": "MY_TEST_EVENT",
                    "EventBusName": "magic-bus",
                    "Resources": ["Yy", "ZZ"],
                    "Source": "orgin",
                }
            ]
        )

    def test_register_saves_event_in_right_place(self) -> None:
        assert self.event_api.get_all_pending_events() == []

        event_1 = MyTestEvent({"x": 1})
        event_2 = MyTestEvent({"x": 2})

        self.event_api.register(event_1)
        self.event_api.register(event_2)

        assert self.event_api.get_all_pending_events() == [event_1, event_2]

    @patch.object(Boto3Client, "eventbridge")
    def test_send(self, mock_send: MagicMock) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        self.event_api.send()

        mock_send.put_events.assert_called_once_with(
            Entries=[
                {
                    "Detail": '{"x": 1}',
                    "DetailType": "MY_TEST_EVENT",
                    "EventBusName": "million-dollar-lambda-event-bus",
                    "Resources": [],
                    "Source": "million-dollar-lambda",
                }
            ]
        )
        assert self.event_api.get_all_sent_events() == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test__send__sends_events_in_chunks_respecting_limits(self, mock_send: MagicMock) -> None:
        for i in range(33):  # AWS allows sending maximum 10 events at once
            self.event_api.register(MyTestEvent({"x": i}))

        self.event_api.send()

        assert mock_send.put_events.call_count == 4
        assert len(mock_send.put_events.call_args_list[0].kwargs["Entries"]) == 10
        assert len(mock_send.put_events.call_args_list[1].kwargs["Entries"]) == 10
        assert len(mock_send.put_events.call_args_list[2].kwargs["Entries"]) == 10
        assert len(mock_send.put_events.call_args_list[3].kwargs["Entries"]) == 3
        assert len(self.event_api.get_all_sent_events()) == 33
        assert len(self.event_api.get_all_pending_events()) == 0
        assert len(self.event_api.get_all_failed_events()) == 0

    @patch.object(Boto3Client, "eventbridge")
    def test__send__stops_processing_events_on_first_error(self, mock_send: MagicMock) -> None:
        mock_send.put_events.side_effect = (None, None, RuntimeError)
        for i in range(33):  # AWS allows sending maximum 10 events at once
            self.event_api.register(MyTestEvent({"x": i}))

        with pytest.raises(RuntimeError):
            self.event_api.send()

        assert mock_send.put_events.call_count == 3
        assert len(self.event_api.get_all_sent_events()) == 20
        assert len(self.event_api.get_all_pending_events()) == 0
        assert len(self.event_api.get_all_failed_events()) == 13

    @patch.object(Boto3Client, "eventbridge")
    def test_sent_fail_saves_events_in_right_place(self, mock_send: MagicMock) -> None:
        assert self.event_api.get_all_failed_events() == []

        mock_send.put_events.side_effect = NotADirectoryError
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        with pytest.raises(NotADirectoryError):
            self.event_api.send()

        assert self.event_api.get_all_failed_events() == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test_send_no_events(self, mock_send: MagicMock) -> None:
        self.event_api.send()

        mock_send.put_events.assert_not_called()
        assert self.event_api.get_all_failed_events() == []
        assert self.event_api.get_all_sent_events() == []
        assert self.event_api.get_all_pending_events() == []

    @patch.object(Boto3Client, "eventbridge")
    def test_singleton_pattern_working_correctly_for_event_api(self, mock_send: MagicMock) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        event_api_1 = EventAPI()
        event_api_2 = EventAPI()
        event_api_2.set_source("XXX")
        event_api_2.set_resources(["a", "b"])
        event_api_3 = EventAPI()

        event_api_3.send()

        assert event_api_1 is event_api_2 is event_api_3 is self.event_api
        mock_send.put_events.assert_called_once_with(
            Entries=[
                {
                    "Detail": '{"x": 1}',
                    "DetailType": "MY_TEST_EVENT",
                    "EventBusName": "million-dollar-lambda-event-bus",
                    "Resources": ["a", "b"],
                    "Source": "XXX",
                }
            ]
        )

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test_second_send_clears_everything(self) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        self.event_api.send()
        self.event_api.send()

        assert self.event_api.get_all_failed_events() == []
        assert self.event_api.get_all_sent_events() == []
        assert self.event_api.get_all_pending_events() == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test_clear(self) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        self.event_api.send()
        self.event_api.register(event)

        self.event_api.clear()

        assert self.event_api.get_all_failed_events() == []
        assert self.event_api.get_all_sent_events() == []
        assert self.event_api.get_all_pending_events() == []
