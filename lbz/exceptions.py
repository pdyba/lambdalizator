#!/usr/local/bin/python3.8
# coding=utf-8
from http import HTTPStatus

from lbz.misc import get_logger
from lbz.response import Response

logger = get_logger(__name__)


class LambdaFWException(Exception):
    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message: str = ""):
        if message:
            self.message = message

    def get_response(self, request_id: str) -> Response:
        return Response(
            {"message": self.message, "request_id": request_id},
            status_code=self.status_code,
            headers={"Content-Type": "application/json"},
        )


class AccessDenied(LambdaFWException):
    """Request forbidden -- authorization will not help"""

    message = HTTPStatus.FORBIDDEN.description
    status_code = HTTPStatus.FORBIDDEN.value


class BadRequestError(LambdaFWException):
    """Bad request syntax or unsupported method"""

    message = HTTPStatus.BAD_REQUEST.description
    status_code = HTTPStatus.BAD_REQUEST.value


class InvalidResolutionError(LambdaFWException):
    """Unaccepted image resolution"""

    message = "Unaccepted image resolution"
    status_code = HTTPStatus.BAD_REQUEST.value


class ServerError(LambdaFWException):
    """Server got itself in trouble"""

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message: str = "", log_msg: str = None):
        super().__init__(message)
        if log_msg:
            logger.error(log_msg)


class NotFound(LambdaFWException):
    """Nothing matches the given URI"""

    message = HTTPStatus.NOT_FOUND.description
    status_code = HTTPStatus.NOT_FOUND.value


class PermissionDenied(LambdaFWException):
    """Request forbidden -- authorization will not help"""

    message = HTTPStatus.FORBIDDEN.description
    status_code = HTTPStatus.FORBIDDEN.value


class UnsupportedMethod(LambdaFWException):
    """Unsupported method: <method>"""

    status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    def __init__(self, method):
        self.message = "Unsupported method: %s" % method


class Unauthorized(LambdaFWException):
    """No permission -- see authorization schemes"""

    message = HTTPStatus.UNAUTHORIZED.description
    status_code = HTTPStatus.UNAUTHORIZED.value


class NotAcceptable(LambdaFWException):
    """URI not available in preferred format"""

    message = HTTPStatus.NOT_ACCEPTABLE.description
    status_code = HTTPStatus.NOT_ACCEPTABLE.value


class SecurityRiskWarning(Warning):
    pass
