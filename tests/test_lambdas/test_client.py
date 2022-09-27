import json
import logging
from io import BytesIO
from typing import Optional
from unittest.mock import MagicMock

import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from lbz.aws_boto3 import Boto3Client
from lbz.lambdas import LambdaClient, LambdaError, LambdaResult


@pytest.fixture(name="lambda_client")
def lambda_client_fixture(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(Boto3Client, "lambda_")


@pytest.mark.parametrize(
    "data, expected_data_bytes",
    [
        ({"sequence": {1, 2, 3}}, b'{"sequence": [1, 2, 3]}'),
        ({"sequence": frozenset({1, 2, 3})}, b'{"sequence": [1, 2, 3]}'),
        (None, b"null"),
    ],
)
def test__invoke__returns_response_sending_provided_data_as_payload(
    lambda_client: MagicMock, data: Optional[dict], expected_data_bytes: bytes
) -> None:
    response_payload = {"result": LambdaResult.OK, "data": "test"}
    lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": BytesIO(json.dumps(response_payload).encode("utf-8")),
    }

    actual_response = LambdaClient.invoke("test-func", "test-op", data)

    assert actual_response == response_payload
    lambda_client.invoke.assert_called_with(
        FunctionName="test-func",
        Payload=(
            b'{"invoke_type": "direct_lambda_request", "op": "test-op", "data": %b}'
            % expected_data_bytes
        ),
        InvocationType="RequestResponse",
    )


@pytest.mark.parametrize(
    "result",
    [
        LambdaResult.BAD_REQUEST,
        LambdaResult.NOT_FOUND,
        LambdaResult.UNAUTHORIZED,
        LambdaResult.CONTRACT_ERROR,
        LambdaResult.SERVER_ERROR,
    ],
)
def test__invoke__returns_response_by_default_even_if_there_is_error_but_logging_it(
    result: str, lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    response_payload = {"result": result, "message": "test"}
    lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": BytesIO(json.dumps(response_payload).encode("utf-8")),
    }

    actual_response = LambdaClient.invoke("test-func", "test-op", {"test": "data"})

    assert actual_response == response_payload
    logged_record = caplog.records[0]
    assert logged_record.levelno == logging.ERROR
    assert logged_record.message == f"Error response from test-func Lambda (op: test-op): {result}"
    assert logged_record.data == {"test": "data"}
    assert logged_record.response == response_payload


@pytest.mark.parametrize("result", LambdaResult.soft_errors())
def test__invoke__does_not_log_message_about_soft_errors_when_they_are_allowed_directly(
    result: str, lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    lambda_client.invoke.return_value = {"Payload": BytesIO(b'{"result": "%s"}' % result.encode())}

    LambdaClient.invoke("test-func", "test-op", allowed_error_results=LambdaResult.soft_errors())

    assert caplog.messages == []


def test__invoke__respects_list_of_allowed_errors_by_logging_all_others(
    lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    result = LambdaResult.BAD_REQUEST
    lambda_client.invoke.return_value = {"Payload": BytesIO(b'{"result": "%s"}' % result.encode())}

    LambdaClient.invoke("test-func", "test-op", allowed_error_results=[LambdaResult.NOT_FOUND])

    assert caplog.messages == [f"Error response from test-func Lambda (op: test-op): {result}"]


@pytest.mark.parametrize("result", LambdaResult.hard_errors())
def test__invoke__does_not_allow_to_bypass_logging_of_hard_errors(
    result: str, lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    lambda_client.invoke.return_value = {"Payload": BytesIO(b'{"result": "%s"}' % result.encode())}

    LambdaClient.invoke("test-func", "test-op", allowed_error_results=LambdaResult.hard_errors())

    assert caplog.messages == [f"Error response from test-func Lambda (op: test-op): {result}"]


@pytest.mark.parametrize("result", LambdaResult.successes())
def test__invoke__returns_response_when_result_is_recognized_as_success(
    result: str, lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    response_payload = {"result": result, "message": "test"}
    lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": BytesIO(json.dumps(response_payload).encode("utf-8")),
    }

    actual_response = LambdaClient.invoke("test-func", "test-op", raise_if_error_resp=True)

    assert actual_response == response_payload
    assert caplog.messages == []


@pytest.mark.parametrize(
    "result",
    [
        LambdaResult.BAD_REQUEST,
        LambdaResult.NOT_FOUND,
        LambdaResult.CONTRACT_ERROR,
        LambdaResult.SERVER_ERROR,
    ],
)
def test__invoke__raises_exception_on_error_response_when_requested_directly(
    result: str, lambda_client: MagicMock
) -> None:
    response_payload = {"result": result, "message": "test"}
    lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": BytesIO(json.dumps(response_payload).encode("utf-8")),
    }

    expected_error_message = rf"Error response from test-func Lambda \(op: test-op\): {result}"
    with pytest.raises(LambdaError, match=expected_error_message) as err:
        LambdaClient.invoke("test-func", "test-op", raise_if_error_resp=True)

    assert err.value.result == result
    assert err.value.response == response_payload


@pytest.mark.parametrize("result", LambdaResult.soft_errors())
def test__invoke__does_not_raise_soft_errors_when_they_are_allowed_directly(
    result: str, lambda_client: MagicMock
) -> None:
    lambda_client.invoke.return_value = {"Payload": BytesIO(b'{"result": "%s"}' % result.encode())}

    LambdaClient.invoke(
        function_name="test-func",
        op="test-op",
        allowed_error_results=LambdaResult.soft_errors(),
        raise_if_error_resp=True,
    )


def test__invoke__respects_list_of_allowed_errors_by_raising_all_others(
    lambda_client: MagicMock,
) -> None:
    result = LambdaResult.BAD_REQUEST
    lambda_client.invoke.return_value = {"Payload": BytesIO(b'{"result": "%s"}' % result.encode())}

    with pytest.raises(LambdaError):
        LambdaClient.invoke(
            function_name="test-func",
            op="test-op",
            allowed_error_results=[LambdaResult.NOT_FOUND],
            raise_if_error_resp=True,
        )


@pytest.mark.parametrize("result", LambdaResult.hard_errors())
def test__invoke__does_not_allow_to_bypass_raising_of_hard_errors(
    result: str, lambda_client: MagicMock
) -> None:
    lambda_client.invoke.return_value = {"Payload": BytesIO(b'{"result": "%s"}' % result.encode())}

    with pytest.raises(LambdaError):
        LambdaClient.invoke(
            function_name="test-func",
            op="test-op",
            allowed_error_results=LambdaResult.hard_errors(),
            raise_if_error_resp=True,
        )


def test__invoke__raises_error_when_response_could_not_be_read_correctly(
    lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    response = {"StatusCode": 200, "Payload": "invalid-payload"}
    lambda_client.invoke.return_value = response

    with pytest.raises(AttributeError):  # type of error does not matter here
        LambdaClient.invoke("test-func", "test-op", raise_if_error_resp=False)

    logged_record = caplog.records[0]
    assert logged_record.message == "Invalid response received from test-func Lambda (op: test-op)"
    assert logged_record.data is None
    assert logged_record.response == response


def test__invoke__returns_accepted_result_when_invoked_asynchronously(
    lambda_client: MagicMock, caplog: LogCaptureFixture
) -> None:
    # Lambda invoked asynchronously only includes a status code in the response
    lambda_client.invoke.return_value = {"StatusCode": 202}

    result = LambdaClient.invoke("test-function", "test-op", asynchronous=True)

    assert result == {"result": LambdaResult.ACCEPTED}
    assert caplog.messages == []
