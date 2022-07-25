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
from lbz.response import Response


def test_lambda_fw_exception() -> None:
    exp = LambdaFWException(message="Nope")
    assert str(exp) == "[500] Nope"
    assert exp.message == "Nope"
    assert exp.status_code == 500

    response = exp.get_response(request_id="test-req-id")
    assert isinstance(response, Response)
    assert response.body == {"message": "Nope", "request_id": "test-req-id"}


def test_lambda_fw_exception_with_error_code() -> None:
    exp = LambdaFWException(message="Nope", error_code="TEST_ERR")
    assert str(exp) == "[500] TEST_ERR - Nope"
    assert exp.message == "Nope"
    assert exp.error_code == "TEST_ERR"
    assert exp.status_code == 500
    assert exp.get_response(request_id="test-req-id").body == {
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
