from lbz.exceptions import NotFound
from lbz.lambdas import LambdaBroker, LambdaResponse, LambdaResult, lambda_ok_response


def simple_func(*_event: dict) -> LambdaResponse:
    return lambda_ok_response()


class TestEventBroker:
    def test_broker_works_properly_when_data_is_provided(self) -> None:
        def func(_event: dict) -> LambdaResponse:
            return lambda_ok_response({"some": "data"})

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}

        resp = LambdaBroker(mapper, event).react()

        assert resp == {
            "result": LambdaResult.OK,
            "data": {"some": "data"},
        }

    def test_broker_works_properly_when_no_data_is_provided(self) -> None:
        mapper = {"x": simple_func}
        event = {"op": "x"}

        resp = LambdaBroker(mapper, event).react()

        assert resp == {
            "result": LambdaResult.OK,
        }

    def test_broker_responds_with_bad_request_event_type_is_not_recognized(self) -> None:
        mapper = {"x": simple_func}
        event = {"op": "y", "data": {"z": 1}}

        response = LambdaBroker(mapper, event).react()

        assert response == {
            "result": LambdaResult.BAD_REQUEST,
            "message": "Handler for y was no implemented",
        }

    def test_broker_responds_no_op_key(self) -> None:
        mapper = {"x": simple_func}
        event = {"data": {"y": 1}}

        resp = LambdaBroker(mapper, event).react()

        assert resp == {
            "result": LambdaResult.BAD_REQUEST,
            "message": "Missing 'op' field in the event.",
        }

    def test_broker_handles_unexpected_lbfw_error_outcome(self) -> None:
        def func(_event: dict) -> LambdaResponse:
            raise NotFound()

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event).react()

        assert resp == {"result": LambdaResult.SERVER_ERROR, "message": NotFound.message}

    def test_broker_handles_unexpected_lbfw_error_outcome_with_error_code(self) -> None:
        class MyNotFound(NotFound):
            error_code = "NN404"

        def func(_event: dict) -> LambdaResponse:
            raise MyNotFound()

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event).react()

        assert resp == {
            "result": LambdaResult.SERVER_ERROR,
            "message": NotFound.message,
            "error_code": "NN404",
        }

    def test_broker_handles_unexpected_error_outcome(self) -> None:
        def func(_event: dict) -> LambdaResponse:
            raise EOFError("oops")

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event).react()

        assert resp == {
            "result": LambdaResult.SERVER_ERROR,
            "message": "EOFError('oops')",
        }
