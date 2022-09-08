import logging
from unittest.mock import MagicMock

from pytest import LogCaptureFixture

from lbz.lambdas.broker import LambdaBroker


class TestEventBroker:
    def test_broker_works_properly(self) -> None:
        func_1 = MagicMock()
        mapper = {"x": func_1}
        event = {"op": "x", "data": {"y": 1}}

        LambdaBroker(mapper, event).handle()  # type: ignore

        func_1.assert_called_once_with({"y": 1})

    def test_broker_responds_not_implemented_when_event_type_is_not_recognized(self) -> None:
        func_1 = MagicMock()
        mapper = {"x": func_1}
        event = {"op": "y", "data": {"z": 1}}

        resp = LambdaBroker(mapper, event).handle()  # type: ignore

        assert resp == {
            "error": (
                "Lambda execution error: "
                "NotImplementedError('No handler implemented for operation: y')"
            )
        }

    def test_broker_continues_even_if_one_handler_failed(self, caplog: LogCaptureFixture) -> None:
        func_1 = MagicMock(side_effect=TypeError)

        mapper = {"x": func_1}
        event = {"op": "x", "data": {"y": 1}}

        LambdaBroker(mapper, event).handle()  # type: ignore

        func_1.assert_called_once_with({"y": 1})
        assert caplog.record_tuples == [
            (
                "lbz.lambdas.broker",
                logging.ERROR,
                "Handling event failed, operation: x",
            )
        ]
