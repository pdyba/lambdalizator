import logging
from unittest.mock import MagicMock

import pytest
from pytest import LogCaptureFixture

from lbz.events.broker import Event, EventBroker


class TestEventBroker:
    def test_broker_works_properly(self) -> None:
        func_1 = MagicMock()
        func_2 = MagicMock()
        expected_event = Event(type="x", data={"y": 1})
        mapper = {"x": [func_1, func_2]}
        event = {"detail-type": "x", "detail": {"y": 1}}

        EventBroker(mapper, event).handle()  # type: ignore

        func_1.assert_called_once_with(expected_event)
        func_2.assert_called_once_with(expected_event)

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
        expected_event = Event(type="x", data={"y": 1})
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
