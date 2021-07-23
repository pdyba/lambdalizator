# coding=utf-8
from lbz.exceptions import (
    BadRequestError,
    Conflict,
    ExpectationFailed,
    FailedDependency,
    Gone,
    ImATeapot,
    InvalidResolutionError,
    LambdaFWException,
    LengthRequired,
    Locked,
    MisdirectedRequest,
    NotAcceptable,
    NotFound,
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
    TooManyRequests,
    URITooLong,
    Unauthorized,
    UnavailableForLegalReasons,
    UnprocessableEntity,
    UnsupportedMediaType,
    UnsupportedMethod,
    UpgradeRequired,
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
        BadRequestError,
        Conflict,
        ExpectationFailed,
        FailedDependency,
        Gone,
        ImATeapot,
        InvalidResolutionError,
        LengthRequired,
        Locked,
        MisdirectedRequest,
        NotAcceptable,
        NotFound,
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
        TooManyRequests,
        URITooLong,
        Unauthorized,
        UnavailableForLegalReasons,
        UnprocessableEntity,
        UnsupportedMediaType,
        UpgradeRequired,
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
