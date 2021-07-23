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
    NotImplementedHTTP,
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
    exp = LambdaFWException("Nope")
    assert exp.message == "Nope"
    assert exp.status_code == 500
    assert isinstance(exp.get_response(request_id=""), Response)


def test_unsupported_method():
    exp = UnsupportedMethod("GET")
    assert exp.message == "Unsupported method: GET"
    assert exp.status_code == 405


@pytest.mark.parametrize(
    "an_excetption",
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
        NotImplementedHTTP,
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
def test_all_exceptions(an_excetption):
    exp = an_excetption()
    code, msg = exp.__doc__.split(" - ")
    assert exp.message == msg.strip()
    assert exp.status_code == int(code)


def test_security_warning():
    warn = SecurityRiskWarning()
    assert isinstance(warn, Warning)
