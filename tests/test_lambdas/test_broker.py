from unittest.mock import MagicMock

from lbz.lambdas.broker import LambdaBroker


class TestEventBroker:
    def test_broker_works_properly(self) -> None:
        func_1 = MagicMock(return_value="some_data")
        mapper = {"x": func_1}
        event = {"op": "x", "data": {"y": 1}}

        resp = LambdaBroker(mapper, event).react()  # type: ignore

        assert resp == "some_data"
        func_1.assert_called_once_with({"y": 1})

    def test_broker_responds_not_implemented_when_event_type_is_not_recognized(self) -> None:
        func_1 = MagicMock()
        mapper = {"x": func_1}
        event = {"op": "y", "data": {"z": 1}}

        resp = LambdaBroker(mapper, event).react()  # type: ignore

        assert resp == {
            "error_code": None,
            "result": "BAD_REQUEST",
            "error": "Lambda execution error: No handler implemented for operation: y",
        }

    def test_broker_responds_no_op_key(self) -> None:
        func_1 = MagicMock()

        mapper = {"x": func_1}
        event = {"data": {"y": 1}}

        resp = LambdaBroker(mapper, event).react()  # type: ignore

        func_1.assert_not_called()
        assert resp == {
            "error_code": None,
            "result": "BAD_REQUEST",
            "error": "Lambda execution error: Missing 'op' field in the event.",
        }
