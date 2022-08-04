import logging
from unittest.mock import MagicMock

import pytest
from pytest import LogCaptureFixture

from lbz.events.broker import EventBroker
from lbz.events.event import Event


class TestEventBroker:
    def test_broker_works_properly(self) -> None:
        func_1 = MagicMock()
        func_2 = MagicMock()
        expected_event = Event({"y": 1}, event_type="x")
        mapper = {"x": [func_1, func_2]}
        event = {"detail-type": "x", "detail": {"y": 1}}

        EventBroker(mapper, event).handle()  # type: ignore

        func_1.assert_called_once_with(expected_event)
        func_2.assert_called_once_with(expected_event)

    def test_broker_works_properly_when_using_type_and_data_optional_keys(self) -> None:
        func_1 = MagicMock()
        expected_event = Event({"y": 1}, event_type="x")
        mapper = {"x": [func_1]}
        event = {"my-type-key": "x", "my-data-key": {"y": 1}}

        EventBroker(
            mapper,  # type: ignore
            event,
            type_key="my-type-key",
            data_key="my-data-key",
        ).handle()

        func_1.assert_called_once_with(expected_event)

    def test_broker_raises_not_implemented_when_event_type_is_not_recognized(self) -> None:
        func_1 = MagicMock()
        func_2 = MagicMock()
        mapper = {"x": [func_1, func_2]}
        event = {"detail-type": "y", "detail": {"y": 1}}

        with pytest.raises(NotImplementedError, match="No handlers implemented for y"):
            EventBroker(mapper, event).handle()  # type: ignore

        func_1.assert_not_called()
        func_2.assert_not_called()

    def test_broker_continues_even_if_one_handler_failed(self, caplog: LogCaptureFixture) -> None:
        func_1 = MagicMock()
        func_2 = MagicMock(side_effect=TypeError)
        func_3 = MagicMock()
        expected_event = Event({"y": 1}, event_type="x")
        mapper = {"x": [func_1, func_2, func_3]}
        event = {"detail-type": "x", "detail": {"y": 1}}

        EventBroker(mapper, event).handle()  # type: ignore

        func_1.assert_called_once_with(expected_event)
        func_2.assert_called_once_with(expected_event)
        func_3.assert_called_once_with(expected_event)
        assert caplog.record_tuples == [
            (
                "lbz.events.broker",
                logging.ERROR,
                "Handling event failed, event: Event(type='x', data={'y': 1})",
            )
        ]
