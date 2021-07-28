# coding=utf-8
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
    SecurityRiskWarning,
    ServerError,
    ServiceUnavailable,
    TooManyRequests,
    URITooLong,
    Unauthorized,
    UnavailableForLegalReasons,
    UnprocessableEntity,
    UnsupportedMediaType,
    UnsupportedMethod,
    UpgradeRequired,
    VariantAlsoNegotiates,
)
from lbz.response import Response
import pytest


def test_lambda_fw_exception():
    exp = LambdaFWException(message="Nope")
    assert exp.message == "Nope"
    assert exp.status_code == 500
    assert isinstance(exp.get_response(request_id=""), Response)


def test_unsupported_method():
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
def test_custom_exception(custom_exception):
    exp = custom_exception()
    try:
        code, msg = exp.__doc__.split(" - ")
    except ValueError:
        code, msg = exp.__doc__.strip(" -"), ""

    assert issubclass(custom_exception, LambdaFWException)
    assert exp.message == msg.strip()
    assert exp.status_code == int(code)


def test_security_warning():
    warn = SecurityRiskWarning()
    assert isinstance(warn, Warning)
