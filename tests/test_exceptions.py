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


def test__lambda_fw_exception__simulates_server_error_by_default() -> None:
    exception = LambdaFWException()

    # this exception should only be used as a base class for all the other more specific ones
    assert str(exception) == "[500] Server got itself in trouble"
    assert exception.message == "Server got itself in trouble"
    assert exception.error_code is None
    assert exception.status_code == 500
    assert exception.get_response(request_id="test-req-id").body == {
        "message": "Server got itself in trouble",
        "request_id": "test-req-id",
    }


def test__lambda_fw_exception__respects_attributes_declared_on_inherited_class_level() -> None:
    class TestException(LambdaFWException):
        message = "No error message"
        status_code = 444
        error_code = "TEST_ERR"

    exception = TestException()

    assert str(exception) == "[444] TEST_ERR - No error message"
    assert exception.message == "No error message"
    assert exception.error_code == "TEST_ERR"
    assert exception.status_code == 444
    assert exception.get_response(request_id="test-req-id").body == {
        "error_code": "TEST_ERR",
        "message": "No error message",
        "request_id": "test-req-id",
    }


def test__lambda_fw_exception__respects_values_provided_during_initialization() -> None:
    exception = LambdaFWException(message="Test error message", error_code="TEST_ERR")

    assert str(exception) == "[500] TEST_ERR - Test error message"
    assert exception.message == "Test error message"
    assert exception.error_code == "TEST_ERR"
    assert exception.status_code == 500
    assert exception.get_response(request_id="test-req-id").body == {
        "error_code": "TEST_ERR",
        "message": "Test error message",
        "request_id": "test-req-id",
    }


def test__unsupported_method__builds_message_based_on_method_provided_from_outside() -> None:
    exception = UnsupportedMethod("GET")

    assert exception.message == "Unsupported method: GET"
    assert exception.error_code is None
    assert exception.status_code == 405


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
def test__custom_exception__contains_message_and_status_code_according_to_its_docstring(
    custom_exception: Type[LambdaFWException],
) -> None:
    exception = custom_exception()
    try:
        code, message = exception.__doc__.split(" - ")
    except ValueError:  # black removes the intentional white space
        code, message = exception.__doc__.split(" -")

    assert issubclass(custom_exception, LambdaFWException)
    assert exception.message == message
    assert exception.status_code == int(code)
