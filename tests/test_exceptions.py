# coding=utf-8
from lbz.exceptions import (
    LambdaFWException,
    AccessDenied,
    BadRequestError,
    InvalidResolutionError,
    ServerError,
    NotFound,
    PermissionDenied,
    UnsupportedMethod,
    Unauthorized,
    RequestTimeout,
)
from lbz.response import Response


def test_lambda_fw_exception():
    exp = LambdaFWException("Nope")
    assert exp.message == "Nope"
    assert exp.status_code == 500
    assert isinstance(exp.get_response(request_id=""), Response)


def test_access_denied():
    exp = AccessDenied()
    assert exp.message == "Request forbidden -- authorization will not help"
    assert exp.status_code == 403


def test_bad_request_error():
    exp = BadRequestError()
    assert exp.message == "Bad request syntax or unsupported method"
    assert exp.status_code == 400


def test_invalid_resolution_error():
    exp = InvalidResolutionError()
    assert exp.message == "Unaccepted image resolution"
    assert exp.status_code == 400


def test_server_error():
    exp = ServerError()
    assert exp.message == "Server got itself in trouble"
    assert exp.status_code == 500


def test_not_found():
    exp = NotFound()
    assert exp.message == "Nothing matches the given URI"
    assert exp.status_code == 404


def test_permission_denied():
    exp = PermissionDenied()
    assert exp.message == "Request forbidden -- authorization will not help"
    assert exp.status_code == 403


def test_unsupported_method():
    exp = UnsupportedMethod("GET")
    assert exp.message == "Unsupported method: GET"
    assert exp.status_code == 405


def test_unauthorized():
    exp = Unauthorized()
    assert exp.message == "No permission -- see authorization schemes"
    assert exp.status_code == 401


def test_request_timeout():
    exp = RequestTimeout()
    assert exp.message == "Request timed out; try again later"
    assert exp.status_code == 408
