#!/usr/local/bin/python3.8
# coding=utf-8
"""
Exceptions.
"""
from http import HTTPStatus

from lbz.response import Response


class LambdaFWException(Exception):
    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    headers = {}
    resp = None

    def __init__(self, message=""):
        if message:
            self.message = message

    def get_resp(self):
        self.resp = Response(
            {"message": self.message},
            status_code=self.status_code,
            headers=self.headers,
        )
        return self.resp

    def to_dict(self):
        if self.resp is None:
            self.get_resp()
        return self.resp.to_dict()


class AccessDenied(LambdaFWException):
    """
    'Request forbidden -- authorization will not help'
    403
    """

    message = HTTPStatus.FORBIDDEN.description
    status_code = HTTPStatus.FORBIDDEN.value


class BadRequestError(LambdaFWException):
    """
    'Bad request syntax or unsupported method'
    """

    message = HTTPStatus.BAD_REQUEST.description
    status_code = HTTPStatus.BAD_REQUEST.value


class InvalidResolutionError(LambdaFWException):
    """
    Unaccepted image resolution
    """

    message = "Unaccepted image resolution"
    status_code = HTTPStatus.BAD_REQUEST.value


class ServerError(LambdaFWException):
    """
    Server got itself in trouble

    """

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value


class NotFound(LambdaFWException):
    """
    Nothing matches the given URI
    404
    """

    message = HTTPStatus.NOT_FOUND.description
    status_code = HTTPStatus.NOT_FOUND.value


class PermissionDenied(LambdaFWException):
    """
    Request forbidden -- authorization will not help
    """

    message = HTTPStatus.FORBIDDEN.description
    status_code = HTTPStatus.FORBIDDEN.value


class UnsupportedMethod(LambdaFWException):
    """
    Unsupported method: <method>

    """

    status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    def __init__(self, method):
        self.message = "Unsupported method: %s" % method


class WrongURI(LambdaFWException):
    """
    Server is not able to produce a response
    """

    message = HTTPStatus.MISDIRECTED_REQUEST.description
    status_code = HTTPStatus.MISDIRECTED_REQUEST.value


class Unauthorized(LambdaFWException):
    """
    No permission -- see authorization schemes
    401
    """

    message = HTTPStatus.UNAUTHORIZED.description
    status_code = HTTPStatus.UNAUTHORIZED.value
