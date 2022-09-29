from unittest.mock import MagicMock

from lbz.exceptions import NotFound
from lbz.lambdas import LambdaBroker, LambdaResult


class TestEventBroker:
    def test_broker_works_properly(self) -> None:
        func_1 = MagicMock(return_value="some_data")
        mapper = {"x": func_1}
        event = {"op": "x", "data": {"y": 1}}

        resp = LambdaBroker(mapper, event).react()  # type: ignore

        assert resp == "some_data"
        func_1.assert_called_once_with({"y": 1})

    def test_broker_raises_error_when_event_type_is_not_recognized(self) -> None:
        func_1 = MagicMock()
        mapper = {"x": func_1}
        event = {"op": "y", "data": {"z": 1}}

        response = LambdaBroker(mapper, event).react()  # type: ignore

        assert response == {
            "result": LambdaResult.SERVER_ERROR,
            "message": "NotImplementedError('y was no implemented')",
        }

    def test_broker_responds_no_op_key(self) -> None:
        func_1 = MagicMock()

        mapper = {"x": func_1}
        event = {"data": {"y": 1}}

        resp = LambdaBroker(mapper, event).react()  # type: ignore

        func_1.assert_not_called()
        assert resp == {
            "result": LambdaResult.BAD_REQUEST,
            "message": "Lambda execution error: Missing 'op' field in the event.",
        }

    def test_broker_handles_expected_error_outcome(self) -> None:
        def func_1(_event: dict) -> None:
            raise NotFound()

        mapper = {"x": func_1}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event).react()  # type: ignore

        assert resp == {"result": LambdaResult.SERVER_ERROR, "message": NotFound.message}

    def test_broker_handles_unexpected_error_outcome(self) -> None:
        def func_1(_event: dict) -> None:
            raise EOFError("oops")

        mapper = {"x": func_1}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event).react()  # type: ignore

        assert resp == {
            "result": LambdaResult.SERVER_ERROR,
            "message": "EOFError('oops')",
        }
