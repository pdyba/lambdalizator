import logging
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from lbz.aws_boto3 import Boto3Client
from lbz.events.api import EventAPI, event_emitter
from lbz.events.event import Event


class MyTestEvent(Event):
    type = "MY_TEST_EVENT"


class TestEventAPI:
    def setup_method(self) -> None:
        # pylint: disable= attribute-defined-outside-init
        self.event_api = EventAPI()

    def teardown_method(self, _test_method: Callable) -> None:
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

    def test__sent_events__disallows_changing_its_content_outside_api(self) -> None:
        self.event_api.sent_events.append(MyTestEvent({"x": 0}))

        assert self.event_api.sent_events == []

    def test__pending_events__disallows_changing_its_content_outside_api(self) -> None:
        self.event_api.pending_events.append(MyTestEvent({"x": 0}))

        assert self.event_api.pending_events == []

    def test__failed_events__disallows_changing_its_content_outside_api(self) -> None:
        self.event_api.failed_events.append(MyTestEvent({"x": 0}))

        assert self.event_api.failed_events == []

    def test_register_saves_event_in_right_place(self) -> None:
        assert self.event_api.pending_events == []

        event_1 = MyTestEvent({"x": 1})
        event_2 = MyTestEvent({"x": 2})

        self.event_api.register(event_1)
        self.event_api.register(event_2)

        assert self.event_api.pending_events == [event_1, event_2]

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
        assert self.event_api.sent_events == [event]

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
        assert len(self.event_api.sent_events) == 33
        assert not self.event_api.pending_events
        assert not self.event_api.failed_events

    @patch.object(Boto3Client, "eventbridge")
    def test__send__always_tries_to_send_all_events_treating_each_chunk_individually(
        self, mock_send: MagicMock, caplog: LogCaptureFixture
    ) -> None:
        mock_send.put_events.side_effect = (
            None,  # no error == success
            ValueError("Event data is too big to be sent"),
            None,  # no error == success
            ValueError("Event type cannot be recognized"),
        )
        for i in range(33):  # AWS allows sending maximum 10 events at once
            self.event_api.register(MyTestEvent({"x": i}))

        error_message = "Sending events has failed. Check logs for more details!"
        with pytest.raises(RuntimeError, match=error_message):
            self.event_api.send()

        assert mock_send.put_events.call_count == 4
        assert len(self.event_api.sent_events) == 20
        assert not self.event_api.pending_events
        assert len(self.event_api.failed_events) == 13
        assert caplog.record_tuples == [
            ("lbz.events.api", logging.ERROR, "Event data is too big to be sent"),
            ("lbz.events.api", logging.ERROR, "Event type cannot be recognized"),
        ]

    @patch.object(Boto3Client, "eventbridge")
    def test_sent_fail_saves_events_in_right_place(self, mock_send: MagicMock) -> None:
        assert self.event_api.failed_events == []

        mock_send.put_events.side_effect = NotADirectoryError
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        with pytest.raises(RuntimeError):
            self.event_api.send()

        assert self.event_api.failed_events == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test_send_no_events(self, mock_send: MagicMock) -> None:
        self.event_api.send()

        mock_send.put_events.assert_not_called()
        assert self.event_api.failed_events == []
        assert self.event_api.sent_events == []
        assert self.event_api.pending_events == []

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

    @patch.object(Boto3Client, "eventbridge")
    def test__send__raises_error_only_when_particular_attempt_failed(
        self, mock_send: MagicMock
    ) -> None:
        mock_send.put_events.side_effect = [NotADirectoryError, None]
        event = MyTestEvent({"x": 1})

        self.event_api.register(event)
        with pytest.raises(RuntimeError):
            self.event_api.send()
        self.event_api.register(event)
        self.event_api.register(event)
        self.event_api.send()

        assert self.event_api.failed_events == [event]
        assert self.event_api.sent_events == [event, event]
        assert self.event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test__send__continuously_extends_lists_of_events_during_next_attempts(self) -> None:
        event_1 = MyTestEvent({"x": 1})
        event_2 = MyTestEvent({"x": 1})
        event_3 = MyTestEvent({"x": 1})

        self.event_api.register(event_1)
        self.event_api.send()
        self.event_api.register(event_2)
        self.event_api.register(event_3)
        self.event_api.send()

        assert self.event_api.failed_events == []
        assert self.event_api.sent_events == [event_1, event_2, event_3]
        assert self.event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test_clear(self) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        self.event_api.send()
        self.event_api.register(event)

        self.event_api.clear()

        assert self.event_api.failed_events == []
        assert self.event_api.sent_events == []
        assert self.event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test__clear_pending__clears_only_pending_events(self) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        self.event_api.send()
        self.event_api.register(event)

        self.event_api.clear_pending()

        assert self.event_api.failed_events == []
        assert self.event_api.sent_events == [event]
        assert self.event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test__clear_sent__clears_only_sent_events(self) -> None:
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        self.event_api.send()
        self.event_api.register(event)

        self.event_api.clear_sent()

        assert self.event_api.failed_events == []
        assert self.event_api.sent_events == []
        assert self.event_api.pending_events == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test__clear_failed__clears_only_failed_events(self, mock_send: MagicMock) -> None:
        mock_send.put_events.side_effect = NotADirectoryError
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)
        with pytest.raises(RuntimeError):
            self.event_api.send()
        self.event_api.register(event)

        self.event_api.clear_failed()

        assert self.event_api.failed_events == []
        assert self.event_api.sent_events == []
        assert self.event_api.pending_events == [event]


@patch.object(Boto3Client, "eventbridge", MagicMock())
class TestEventEmitter:
    def test_does_nothing_when_thera_are_no_pending_events(self) -> None:
        @event_emitter
        def decorated_function() -> None:
            pass

        decorated_function()

        assert not EventAPI().sent_events
        assert not EventAPI().pending_events
        assert not EventAPI().failed_events

    def test_sends_all_pending_events_when_decorated_function_finished_with_success(self) -> None:
        @event_emitter
        def decorated_function() -> None:
            EventAPI().register(MyTestEvent({"x": 1}))

        decorated_function()

        assert EventAPI().sent_events == [MyTestEvent({"x": 1})]
        assert not EventAPI().pending_events
        assert not EventAPI().failed_events

    def test_clears_pending_queue_when_error_appeared_during_running_decorated_function(
        self,
    ) -> None:
        @event_emitter
        def decorated_function() -> None:
            EventAPI().register(MyTestEvent({"x": 1}))
            raise RuntimeError

        EventAPI().register(MyTestEvent({"x": 2}))
        EventAPI().send()
        with pytest.raises(RuntimeError):
            decorated_function()

        assert EventAPI().sent_events == [MyTestEvent({"x": 2})]
        assert not EventAPI().pending_events
        assert not EventAPI().failed_events

    def test_always_clears_queues_before_actually_decorating_function(self) -> None:
        EventAPI().register(MyTestEvent({"x": 1}))
        EventAPI().send()
        EventAPI().register(MyTestEvent({"x": 2}))

        @event_emitter
        def decorated_function() -> None:
            pass

        assert not EventAPI().sent_events
        assert not EventAPI().pending_events
        assert not EventAPI().failed_events
