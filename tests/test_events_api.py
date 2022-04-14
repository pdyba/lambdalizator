from os import environ
from typing import Optional
from unittest.mock import MagicMock, patch

from lbz.aws_boto3 import Boto3Client
from lbz.events.api import BaseEvent, EventAPI


class MyTestEvent(BaseEvent):
    type = "MY_TEST_EVENT"


class TestBaseNewEvent:
    def test_base_new_event(self) -> None:
        new_event = MyTestEvent({"x": 1})

        assert hasattr(new_event, "raw_data")
        assert hasattr(new_event, "data")
        assert new_event.type == "MY_TEST_EVENT"
        assert new_event.raw_data == {"x": 1}
        assert new_event.data == '{"x": 1}'


class TestEventApi:
    event_api: Optional[EventAPI] = None

    def setup_method(self) -> None:
        # pylint: disable= attribute-defined-outside-init
        with patch.dict(environ, {"AWS_LAMBDA_FUNCTION_NAME": "million-dollar-lambda"}):
            self.event_api = EventAPI()

    def teardown_method(self, _test_method) -> None:
        # pylint: disable= attribute-defined-outside-init
        self.event_api._del()  # pylint: disable=protected-access
        self.event_api = None

    def test_init_with_defaults(self) -> None:
        # pylint: disable=protected-access
        assert self.event_api._pending_events == []
        assert self.event_api._sent_events == []
        assert self.event_api._source == "million-dollar-lambda"
        assert self.event_api._bus_name == "million-dollar-lambda-event-bus"
        assert self.event_api._resources == []

    def test_set_source(self) -> None:
        # pylint: disable=protected-access
        self.event_api.set_source("XXX")
        assert self.event_api._source == "XXX"

    def test_set_resource(self) -> None:
        # pylint: disable=protected-access
        self.event_api.set_resources(["x", "Y"])
        assert self.event_api._resources == ["x", "Y"]

    def test_register(self) -> None:
        # pylint: disable=protected-access
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        assert self.event_api._pending_events == [event]

    def test_get_all_registered_events(self) -> None:
        event_1 = MyTestEvent({"x": 1})
        event_2 = MyTestEvent({"x": 2})
        self.event_api.register(event_1)
        self.event_api.register(event_2)
        assert self.event_api.get_all_pending_events() == [event_1, event_2]

    @patch.object(Boto3Client, "eventbridge")
    @patch.object(EventAPI, "_mark_sent")
    def test_send(self, mock__mark_sent: MagicMock, mock_send: MagicMock) -> None:
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
        mock__mark_sent.assert_called_once()

    def test_clear(self):
        # pylint: disable=protected-access
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        self.event_api._mark_sent()

        assert self.event_api._pending_events == []
        assert self.event_api._sent_events == [event]

    def test_get_all_sent_events(self):
        event = MyTestEvent({"x": 1})
        self.event_api.register(event)

        self.event_api._mark_sent()  # pylint: disable=protected-access

        assert self.event_api.get_all_sent_events() == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test_send_no_events(self, mock_send: MagicMock) -> None:
        self.event_api.send()

        mock_send.assert_not_called()

    def test_create_eb_entry(self) -> None:
        new_event = MyTestEvent({"x": 1})

        resp = self.event_api._create_eb_entry(new_event)  # pylint: disable=protected-access

        assert resp == {
            "Detail": '{"x": 1}',
            "DetailType": "MY_TEST_EVENT",
            "EventBusName": "million-dollar-lambda-event-bus",
            "Resources": [],
            "Source": "million-dollar-lambda",
        }


class TestEventApiSingleton:
    def test_singleton_pattern_working_correctly_for_event_api(self) -> None:
        event_api_1 = EventAPI()
        event_api_2 = EventAPI()
        event_api_2.set_source("XXX")
        event_api_2.set_resources(["a", "b"])
        event_api_3 = EventAPI()
        assert event_api_3._source == "XXX"  # pylint: disable=protected-access
        assert event_api_3._resources == ["a", "b"]  # pylint: disable=protected-access
        assert event_api_1 == event_api_2 == event_api_3
