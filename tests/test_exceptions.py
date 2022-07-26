# coding=utf-8
from typing import Type

import pytest

from lbz.exceptions import (
    BadGateway,
    BadRequestError,
    Conflict,
    ExpectationFailed,
    FailedDependency,
    GatewayTimeout,
    Gone,
    ImATeapot,
    InsufficientStorage,
    InvalidResolutionError,
    LambdaFWException,
    LengthRequired,
    Locked,
    LoopDetected,
    MisdirectedRequest,
    NetworkAuthenticationRequired,
    NotAcceptable,
    NotExtended,
    NotFound,
    NotImplementedFunctionality,
    PayloadTooLarge,
    PaymentRequired,
    PermissionDenied,
    PreconditionFailed,
    PreconditionRequired,
    ProxyAuthenticationRequired,
    RangeNotSatisfiable,
    RequestHeaderFieldsTooLarge,
    RequestTimeout,
    ServerError,
    ServiceUnavailable,
    TooManyRequests,
    Unauthorized,
    UnavailableForLegalReasons,
    UnprocessableEntity,
    UnsupportedMediaType,
    UnsupportedMethod,
    UpgradeRequired,
    URITooLong,
    VariantAlsoNegotiates,
)


def test_lambda_fw_exception() -> None:
    exception = LambdaFWException(message="Nope")
    assert str(exception) == "[500] Nope"
    assert exception.message == "Nope"
    assert exception.status_code == 500

    response = exception.get_response(request_id="test-req-id")
    assert response.body == {"message": "Nope", "request_id": "test-req-id"}


def test_lambda_fw_exception_with_error_code() -> None:
    class TestException(LambdaFWException):
        error_code = "TEST_ERR"

    exception = TestException(message="Nope")
    assert str(exception) == "[500] TEST_ERR - Nope"
    assert exception.message == "Nope"
    assert exception.error_code == "TEST_ERR"
    assert exception.status_code == 500
    assert exception.get_response(request_id="test-req-id").body == {
        "error_code": "TEST_ERR",
        "message": "Nope",
        "request_id": "test-req-id",
    }


def test_unsupported_method() -> None:
    exp = UnsupportedMethod("GET")
    assert exp.message == "Unsupported method: GET"
    assert exp.status_code == 405


@pytest.mark.parametrize(
    "custom_exception",
    [
        BadGateway,
        BadRequestError,
        Conflict,
        ExpectationFailed,
        FailedDependency,
        GatewayTimeout,
        Gone,
        ImATeapot,
        InsufficientStorage,
        InvalidResolutionError,
        LengthRequired,
        Locked,
        LoopDetected,
        MisdirectedRequest,
        NetworkAuthenticationRequired,
        NotAcceptable,
        NotExtended,
        NotFound,
        NotImplementedFunctionality,
        PayloadTooLarge,
        PaymentRequired,
        PermissionDenied,
        PreconditionFailed,
        PreconditionRequired,
        ProxyAuthenticationRequired,
        RangeNotSatisfiable,
        RequestHeaderFieldsTooLarge,
        RequestTimeout,
        ServerError,
        ServiceUnavailable,
        TooManyRequests,
        URITooLong,
        Unauthorized,
        UnavailableForLegalReasons,
        UnprocessableEntity,
        UnsupportedMediaType,
        UpgradeRequired,
        VariantAlsoNegotiates,
    ],
)
def test_custom_exception(custom_exception: Type[LambdaFWException]) -> None:
    exp = custom_exception()
    try:
        code, msg = exp.__doc__.split(" - ")
    except ValueError:  # black removes the intentional white space
        code, msg = exp.__doc__.split(" -")

    assert issubclass(custom_exception, LambdaFWException)
    assert exp.message == msg.strip()
    assert exp.status_code == int(code)
