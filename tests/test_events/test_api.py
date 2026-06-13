import logging
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from lbz.aws_boto3 import Boto3Client
from lbz.events.api import EventAPI, event_emitter
from lbz.events.event import Event
from lbz.misc import Singleton


class MyTestEvent(Event):
    type = "MY_TEST_EVENT"


@pytest.fixture(name="event_api")
def event_api_fixture() -> Generator[EventAPI]:
    yield EventAPI()
    Singleton.drop_instance(cls=EventAPI)


class TestEventAPI:
    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test___repr__(self, event_api: EventAPI) -> None:
        expected_repr = (
            "<EventAPI bus: million-dollar-lambda-event-bus Events: pending=0 sent=0 failed=0>"
        )
        assert str(event_api) == expected_repr
        event_api.register(MyTestEvent({"x": 1}))
        event_api.register(MyTestEvent({"x": 1}))
        expected_repr = (
            "<EventAPI bus: million-dollar-lambda-event-bus Events: pending=2 sent=0 failed=0>"
        )
        assert str(event_api) == expected_repr
        event_api.send()
        expected_repr = (
            "<EventAPI bus: million-dollar-lambda-event-bus Events: pending=0 sent=2 failed=0>"
        )
        assert str(event_api) == expected_repr

    @patch.object(Boto3Client, "eventbridge")
    def test_settters(self, mock_send: MagicMock, event_api: EventAPI) -> None:
        event = MyTestEvent({"x": 1})
        event_api.register(event)
        event_api.set_resources(["Yy", "ZZ"])
        event_api.set_source("orgin")
        event_api.set_bus_name("magic-bus")

        event_api.send()

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

    def test__sent_events__disallows_changing_its_content_outside_api(
        self, event_api: EventAPI
    ) -> None:
        event_api.sent_events.append(MyTestEvent({"x": 0}))

        assert event_api.sent_events == []

    def test__pending_events__disallows_changing_its_content_outside_api(
        self, event_api: EventAPI
    ) -> None:
        event_api.pending_events.append(MyTestEvent({"x": 0}))

        assert event_api.pending_events == []

    def test__failed_events__disallows_changing_its_content_outside_api(
        self, event_api: EventAPI
    ) -> None:
        event_api.failed_events.append(MyTestEvent({"x": 0}))

        assert event_api.failed_events == []

    def test_register_saves_event_in_right_place(self, event_api: EventAPI) -> None:
        assert event_api.pending_events == []

        event_1 = MyTestEvent({"x": 1})
        event_2 = MyTestEvent({"x": 2})

        event_api.register(event_1)
        event_api.register(event_2)

        assert event_api.pending_events == [event_1, event_2]

    @patch.object(Boto3Client, "eventbridge")
    def test_send(self, mock_send: MagicMock, event_api: EventAPI) -> None:
        event = MyTestEvent({"x": 1})
        event_api.register(event)

        event_api.send()

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
        assert event_api.sent_events == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test__send__sends_events_in_chunks_respecting_limits(
        self, mock_send: MagicMock, event_api: EventAPI
    ) -> None:
        for i in range(33):  # AWS allows sending maximum 10 events at once
            event_api.register(MyTestEvent({"x": i}))

        event_api.send()

        assert mock_send.put_events.call_count == 4
        assert len(mock_send.put_events.call_args_list[0].kwargs["Entries"]) == 10
        assert len(mock_send.put_events.call_args_list[1].kwargs["Entries"]) == 10
        assert len(mock_send.put_events.call_args_list[2].kwargs["Entries"]) == 10
        assert len(mock_send.put_events.call_args_list[3].kwargs["Entries"]) == 3
        assert len(event_api.sent_events) == 33
        assert not event_api.pending_events
        assert not event_api.failed_events

    @patch.object(Boto3Client, "eventbridge")
    def test__send__always_tries_to_send_all_events_treating_each_chunk_individually(
        self, mock_send: MagicMock, event_api: EventAPI, caplog: LogCaptureFixture
    ) -> None:
        mock_send.put_events.side_effect = (
            None,  # no error == success
            ValueError("Event data is too big to be sent"),
            None,  # no error == success
            ValueError("Event type cannot be recognized"),
        )
        for i in range(33):  # AWS allows sending maximum 10 events at once
            event_api.register(MyTestEvent({"x": i}))

        event_api.send()

        assert mock_send.put_events.call_count == 4
        assert len(event_api.sent_events) == 20
        assert len(event_api.pending_events) == 0
        assert len(event_api.failed_events) == 13
        assert caplog.record_tuples == [
            ("lbz.events.api", logging.ERROR, "Event data is too big to be sent"),
            ("lbz.events.api", logging.ERROR, "Event type cannot be recognized"),
        ]

    @patch.object(Boto3Client, "eventbridge")
    def test_sent_fail_saves_events_in_right_place(
        self, mock_send: MagicMock, event_api: EventAPI
    ) -> None:
        assert event_api.failed_events == []

        mock_send.put_events.side_effect = NotADirectoryError
        event = MyTestEvent({"x": 1})
        event_api.register(event)

        event_api.send()

        assert event_api.failed_events == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test_send_no_events(self, mock_send: MagicMock, event_api: EventAPI) -> None:
        event_api.send()

        mock_send.put_events.assert_not_called()
        assert event_api.failed_events == []
        assert event_api.sent_events == []
        assert event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge")
    def test_singleton_pattern_working_correctly_for_event_api(
        self, mock_send: MagicMock, event_api: EventAPI
    ) -> None:
        event = MyTestEvent({"x": 1})
        event_api.register(event)
        event_api_1 = EventAPI()
        event_api_2 = EventAPI()
        event_api_2.set_source("XXX")
        event_api_2.set_resources(["a", "b"])
        event_api_3 = EventAPI()

        event_api_3.send()

        assert event_api_1 is event_api_2 is event_api_3 is event_api
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
    def test__send__continuously_extends_lists_of_events_during_next_attempts(
        self, event_api: EventAPI
    ) -> None:
        event_1 = MyTestEvent({"x": 1})
        event_2 = MyTestEvent({"x": 1})
        event_3 = MyTestEvent({"x": 1})

        event_api.register(event_1)
        event_api.send()
        event_api.register(event_2)
        event_api.register(event_3)
        event_api.send()

        assert event_api.failed_events == []
        assert event_api.sent_events == [event_1, event_2, event_3]
        assert event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test_clear(self, event_api: EventAPI) -> None:
        event = MyTestEvent({"x": 1})
        event_api.register(event)
        event_api.send()
        event_api.register(event)

        event_api.clear()

        assert event_api.failed_events == []
        assert event_api.sent_events == []
        assert event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test__clear_pending__clears_only_pending_events(self, event_api: EventAPI) -> None:
        event = MyTestEvent({"x": 1})
        event_api.register(event)
        event_api.send()
        event_api.register(event)

        event_api.clear_pending()

        assert event_api.failed_events == []
        assert event_api.sent_events == [event]
        assert event_api.pending_events == []

    @patch.object(Boto3Client, "eventbridge", MagicMock())
    def test__clear_sent__clears_only_sent_events(self, event_api: EventAPI) -> None:
        event = MyTestEvent({"x": 1})
        event_api.register(event)
        event_api.send()
        event_api.register(event)

        event_api.clear_sent()

        assert event_api.failed_events == []
        assert event_api.sent_events == []
        assert event_api.pending_events == [event]

    @patch.object(Boto3Client, "eventbridge")
    def test__clear_failed__clears_only_failed_events(
        self, mock_send: MagicMock, event_api: EventAPI
    ) -> None:
        mock_send.put_events.side_effect = NotADirectoryError
        event = MyTestEvent({"x": 1})
        event_api.register(event)
        event_api.send()
        event_api.register(event)

        event_api.clear_failed()

        assert event_api.failed_events == []
        assert event_api.sent_events == []
        assert event_api.pending_events == [event]


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

        with pytest.raises(RuntimeError):
            decorated_function()

        assert not EventAPI().sent_events
        assert not EventAPI().pending_events
        assert not EventAPI().failed_events

    def test_always_clears_queues_before_actually_triggering_function(self) -> None:
        @event_emitter
        def decorated_function() -> None:
            pass

        EventAPI().register(MyTestEvent({"x": 1}))
        EventAPI().send()
        EventAPI().register(MyTestEvent({"x": 2}))
        decorated_function()

        assert not EventAPI().sent_events
        assert not EventAPI().pending_events
        assert not EventAPI().failed_events
