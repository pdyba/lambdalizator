from os import environ
from typing import Optional
from unittest.mock import MagicMock, patch

from lbz.boto3_client import Boto3Clients
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
        assert self.event_api.entries == []
        assert self.event_api._source == "million-dollar-lambda"
        assert self.event_api.bus_name == "million-dollar-lambda-event-bus"
        assert self.event_api._resources == []

    def test_set_source(self) -> None:
        # pylint: disable=protected-access
        self.event_api.set_source("XXX")
        assert self.event_api._source == "XXX"

    def test_set_resource(self) -> None:
        # pylint: disable=protected-access
        self.event_api.set_resource(["x", "Y"])
        assert self.event_api._resources == ["x", "Y"]

    @patch.object(EventAPI, "create_eb_entry")
    def test_register(self, mock_create_eb_entry: MagicMock) -> None:
        mock_create_eb_entry.return_value = True

        self.event_api.register({"x": 1})

        mock_create_eb_entry.assert_called_once_with({"x": 1})
        assert self.event_api.entries == [True]

    def test_get_all_registered_events(self) -> None:
        self.event_api.register(MyTestEvent({"x": 1}))
        self.event_api.register(MyTestEvent({"x": 2}))
        assert self.event_api.get_all_registered_events() == [
            {
                "Detail": '{"x": 1}',
                "DetailType": "MY_TEST_EVENT",
                "EventBusName": "million-dollar-lambda-event-bus",
                "Resources": [],
                "Source": "million-dollar-lambda",
            },
            {
                "Detail": '{"x": 2}',
                "DetailType": "MY_TEST_EVENT",
                "EventBusName": "million-dollar-lambda-event-bus",
                "Resources": [],
                "Source": "million-dollar-lambda",
            },
        ]

    @patch.object(Boto3Clients, "eventbridge")
    def test_send(self, mock_send: MagicMock) -> None:
        self.event_api.register(MyTestEvent({"x": 1}))

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

    @patch.object(Boto3Clients, "eventbridge")
    def test_send_no_events(self, mock_send: MagicMock) -> None:
        self.event_api.send()

        mock_send.assert_not_called()

    def test_create_eb_entry(self) -> None:
        new_event = MyTestEvent({"x": 1})

        resp = self.event_api.create_eb_entry(new_event)

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
        event_api_2.set_resource(["a", "b"])
        event_api_3 = EventAPI()
        assert event_api_3._source == "XXX"  # pylint: disable=protected-access
        assert event_api_3._resources == ["a", "b"]  # pylint: disable=protected-access
        assert event_api_1 == event_api_2 == event_api_3
