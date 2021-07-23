# coding=utf-8
"""
Set of HTTP Exceptions that are json compatabile.
"""
from http import HTTPStatus

from lbz.misc import get_logger
from lbz.response import Response

logger = get_logger(__name__)


class LambdaFWException(Exception):
    """
    Standarised for AWS Lambda exception class.
    """

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message: str = ""):
        super().__init__()
        if message:
            self.message = message

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.message}"

    def get_response(self, request_id: str) -> Response:
        """
        Creates a proper standarised Response for Errors.
        """
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


class RequestTimeout(LambdaFWException):
    """Request timed out -- Request timed out; try again later"""

    message = HTTPStatus.REQUEST_TIMEOUT.description
    status_code = HTTPStatus.REQUEST_TIMEOUT.value


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
        super().__init__("Unsupported method: %s" % method)


class Unauthorized(LambdaFWException):
    """No permission -- see authorization schemes"""

    message = HTTPStatus.UNAUTHORIZED.description
    status_code = HTTPStatus.UNAUTHORIZED.value


class NotAcceptable(LambdaFWException):
    """URI not available in preferred format"""

    message = HTTPStatus.NOT_ACCEPTABLE.description
    status_code = HTTPStatus.NOT_ACCEPTABLE.value


class SecurityRiskWarning(Warning):
    """
    Security Risk Warning
    """
