#!/usr/local/bin/python3.8
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
)
from lbz.response import Response


def test_LambdaFWException():
    exp = LambdaFWException("Nope")
    assert exp.message == "Nope"
    assert exp.status_code == 500
    assert isinstance(exp.get_response(request_id=""), Response)


def test_AccessDenied():
    exp = AccessDenied()
    assert exp.message == "Request forbidden -- authorization will not help"
    assert exp.status_code == 403


def test_BadRequestError():
    exp = BadRequestError()
    assert exp.message == "Bad request syntax or unsupported method"
    assert exp.status_code == 400


def test_InvalidResolutionError():
    exp = InvalidResolutionError()
    assert exp.message == "Unaccepted image resolution"
    assert exp.status_code == 400


def test_ServerError():
    exp = ServerError()
    assert exp.message == "Server got itself in trouble"
    assert exp.status_code == 500


def test_NotFound():
    exp = NotFound()
    assert exp.message == "Nothing matches the given URI"
    assert exp.status_code == 404


def test_PermissionDenied():
    exp = PermissionDenied()
    assert exp.message == "Request forbidden -- authorization will not help"
    assert exp.status_code == 403


def test_UnsupportedMethod():
    exp = UnsupportedMethod("GET")
    assert exp.message == "Unsupported method: GET"
    assert exp.status_code == 405


def test_Unauthorized():
    exp = Unauthorized()
    assert exp.message == "No permission -- see authorization schemes"
    assert exp.status_code == 401
