import logging

from pytest import LogCaptureFixture

from lbz.exceptions import NotFound
from lbz.lambdas import LambdaBroker, LambdaResponse, LambdaResult, lambda_ok_response
from lbz.type_defs import LambdaContext


def simple_func(_data: dict | None = None) -> LambdaResponse:
    return lambda_ok_response()


class TestEventBroker:
    def test_broker_works_properly_when_data_is_provided(self) -> None:
        def func(_data: dict) -> LambdaResponse:
            return lambda_ok_response({"some": "data"})

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}

        resp = LambdaBroker(mapper, event, LambdaContext()).react()

        assert resp == {
            "result": LambdaResult.OK,
            "data": {"some": "data"},
        }

    def test_broker_responds_with_contract_error_when_op_is_not_recognized(
        self, caplog: LogCaptureFixture
    ) -> None:
        mapper = {"x": simple_func}
        event = {"op": "y", "data": {"z": 1}}

        response = LambdaBroker(mapper, event, LambdaContext()).react()

        assert response == {
            "result": LambdaResult.CONTRACT_ERROR,
            "message": '"y" not implemented.',
        }
        assert caplog.record_tuples == [
            (
                "lbz.lambdas.broker",
                logging.ERROR,
                'No handler declared for requested operation: "y"',
            )
        ]

    def test_broker_responds_with_contract_error_when_no_op_key(
        self, caplog: LogCaptureFixture
    ) -> None:
        mapper = {"x": simple_func}
        event = {"data": {"y": 1}}

        resp = LambdaBroker(mapper, event, LambdaContext()).react()

        assert resp == {
            "result": LambdaResult.CONTRACT_ERROR,
            "message": 'Missing "op" field.',
        }
        assert caplog.record_tuples == [
            (
                "lbz.lambdas.broker",
                logging.ERROR,
                "Missing \"op\" field in the processed event: {'data': {'y': 1}}",
            )
        ]

    def test_broker_handles_unexpected_lbz_exception_outcome(
        self, caplog: LogCaptureFixture
    ) -> None:
        def func(_data: dict) -> LambdaResponse:
            raise NotFound()

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event, LambdaContext()).react()

        assert resp == {"result": LambdaResult.SERVER_ERROR, "message": NotFound.message}
        assert caplog.record_tuples == [
            (
                "lbz.lambdas.broker",
                logging.ERROR,
                'Unexpected error in "func" function!',
            )
        ]

    def test_broker_handles_unexpected_lbz_exception_outcome_with_error_code(
        self, caplog: LogCaptureFixture
    ) -> None:
        def func(_data: dict) -> LambdaResponse:
            raise NotFound(error_code="NN404")

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event, LambdaContext()).react()

        assert resp == {
            "result": LambdaResult.SERVER_ERROR,
            "message": NotFound.message,
            "error_code": "NN404",
        }
        assert caplog.record_tuples == [
            (
                "lbz.lambdas.broker",
                logging.ERROR,
                'Unexpected error in "func" function!',
            )
        ]

    def test_broker_handles_unexpected_error_outcome(self, caplog: LogCaptureFixture) -> None:
        def func(_data: dict) -> LambdaResponse:
            raise EOFError("oops")

        mapper = {"x": func}
        event = {"op": "x", "data": {"y": 1}}
        resp = LambdaBroker(mapper, event, LambdaContext()).react()

        assert resp == {
            "result": LambdaResult.SERVER_ERROR,
            "message": "EOFError('oops')",
        }
        assert caplog.record_tuples == [
            (
                "lbz.lambdas.broker",
                logging.ERROR,
                'Unexpected error in "func" function!',
            )
        ]
