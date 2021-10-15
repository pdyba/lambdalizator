# coding=utf-8
"""
Set of HTTP Exceptions that are json compatabile.
"""
from http import HTTPStatus

from lbz.response import Response


class SecurityError(Exception):
    """Request did not match security requirements expected by server."""


class LambdaFWException(Exception):
    """
    Standarised for AWS Lambda exception class.
    """

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
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
        )


class BadRequestError(LambdaFWException):
    """400 - Bad request syntax or unsupported method"""

    message = HTTPStatus.BAD_REQUEST.description
    status_code = HTTPStatus.BAD_REQUEST.value


class InvalidResolutionError(LambdaFWException):
    """400 - Unaccepted image resolution"""

    message = "Unaccepted image resolution"
    status_code = HTTPStatus.BAD_REQUEST.value


class Unauthorized(LambdaFWException):
    """401 - No permission -- see authorization schemes"""

    message = HTTPStatus.UNAUTHORIZED.description
    status_code = HTTPStatus.UNAUTHORIZED.value


class PaymentRequired(LambdaFWException):
    """402 - No payment -- see charging schemes"""

    message = HTTPStatus.PAYMENT_REQUIRED.description
    status_code = HTTPStatus.PAYMENT_REQUIRED.value


class PermissionDenied(LambdaFWException):
    """403 - Request forbidden -- authorization will not help"""

    message = HTTPStatus.FORBIDDEN.description
    status_code = HTTPStatus.FORBIDDEN.value


class NotFound(LambdaFWException):
    """404 - Nothing matches the given URI"""

    message = HTTPStatus.NOT_FOUND.description
    status_code = HTTPStatus.NOT_FOUND.value


class UnsupportedMethod(LambdaFWException):
    """405 - Unsupported method: <method>"""

    status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    def __init__(self, method: str) -> None:
        super().__init__(message="Unsupported method: %s" % method)


class NotAcceptable(LambdaFWException):
    """406 - URI not available in preferred format"""

    message = HTTPStatus.NOT_ACCEPTABLE.description
    status_code = HTTPStatus.NOT_ACCEPTABLE.value


class ProxyAuthenticationRequired(LambdaFWException):
    """407 - You must authenticate with this proxy before proceeding"""

    message = HTTPStatus.PROXY_AUTHENTICATION_REQUIRED.description
    status_code = HTTPStatus.PROXY_AUTHENTICATION_REQUIRED.value


class RequestTimeout(LambdaFWException):
    """408 - Request timed out; try again later"""

    message = HTTPStatus.REQUEST_TIMEOUT.description
    status_code = HTTPStatus.REQUEST_TIMEOUT.value


class Conflict(LambdaFWException):
    """409 - Request conflict"""

    message = HTTPStatus.CONFLICT.description
    status_code = HTTPStatus.CONFLICT.value


class Gone(LambdaFWException):
    """410 - URI no longer exists and has been permanently removed"""

    message = HTTPStatus.GONE.description
    status_code = HTTPStatus.GONE.value


class LengthRequired(LambdaFWException):
    """411 - Client must specify Content-Length"""

    message = HTTPStatus.LENGTH_REQUIRED.description
    status_code = HTTPStatus.LENGTH_REQUIRED.value


class PreconditionFailed(LambdaFWException):
    """412 - Precondition in headers is false"""

    message = HTTPStatus.PRECONDITION_FAILED.description
    status_code = HTTPStatus.PRECONDITION_FAILED.value


class PayloadTooLarge(LambdaFWException):
    """413 - Entity is too large"""

    message = HTTPStatus.REQUEST_ENTITY_TOO_LARGE.description
    status_code = HTTPStatus.REQUEST_ENTITY_TOO_LARGE.value


class URITooLong(LambdaFWException):
    """414 - URI is too long"""

    message = HTTPStatus.REQUEST_URI_TOO_LONG.description
    status_code = HTTPStatus.REQUEST_URI_TOO_LONG.value


class UnsupportedMediaType(LambdaFWException):
    """415 - Entity body in unsupported format"""

    message = HTTPStatus.UNSUPPORTED_MEDIA_TYPE.description
    status_code = HTTPStatus.UNSUPPORTED_MEDIA_TYPE.value


class RangeNotSatisfiable(LambdaFWException):
    """416 - Cannot satisfy request range"""

    message = HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE.description
    status_code = HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE.value


class ExpectationFailed(LambdaFWException):
    """417 - Expect condition could not be satisfied"""

    message = HTTPStatus.EXPECTATION_FAILED.description
    status_code = HTTPStatus.EXPECTATION_FAILED.value


class ImATeapot(LambdaFWException):
    """418 - The server refuses the attempt to brew coffee with a teapot"""

    message = "The server refuses the attempt to brew coffee with a teapot"
    status_code = 418


class MisdirectedRequest(LambdaFWException):
    """421 - Server is not able to produce a response"""

    message = HTTPStatus.MISDIRECTED_REQUEST.description
    status_code = HTTPStatus.MISDIRECTED_REQUEST.value


class UnprocessableEntity(LambdaFWException):
    """422 -"""

    message = HTTPStatus.UNPROCESSABLE_ENTITY.description
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value


class Locked(LambdaFWException):
    """423 -"""

    message = HTTPStatus.LOCKED.description
    status_code = HTTPStatus.LOCKED.value


class FailedDependency(LambdaFWException):
    """424 -"""

    message = HTTPStatus.FAILED_DEPENDENCY.description
    status_code = HTTPStatus.FAILED_DEPENDENCY.value


class UpgradeRequired(LambdaFWException):
    """426 -"""

    message = HTTPStatus.UPGRADE_REQUIRED.description
    status_code = HTTPStatus.UPGRADE_REQUIRED.value


class PreconditionRequired(LambdaFWException):
    """428 - The origin server requires the request to be conditional"""

    message = HTTPStatus.PRECONDITION_REQUIRED.description
    status_code = HTTPStatus.PRECONDITION_REQUIRED.value


class TooManyRequests(LambdaFWException):
    """429 - The user has sent too many requests in a given amount of time ("rate limiting")"""

    message = HTTPStatus.TOO_MANY_REQUESTS.description
    status_code = HTTPStatus.TOO_MANY_REQUESTS.value


class RequestHeaderFieldsTooLarge(LambdaFWException):
    """431 - The server is unwilling to process the request because its header fields are too large"""

    message = HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE.description
    status_code = HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE.value


class UnavailableForLegalReasons(LambdaFWException):
    """451 - The server is denying access to the resource as a consequence of a legal demand"""

    message = HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS.description
    status_code = HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS.value


class ServerError(LambdaFWException):
    """500 - Server got itself in trouble"""

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value


class NotImplementedFunctionality(LambdaFWException):
    """501 - Server does not support this operation"""

    message = HTTPStatus.NOT_IMPLEMENTED.description
    status_code = HTTPStatus.NOT_IMPLEMENTED.value


class BadGateway(LambdaFWException):
    """502 - Invalid responses from another server/proxy"""

    message = HTTPStatus.BAD_GATEWAY.description
    status_code = HTTPStatus.BAD_GATEWAY.value


class ServiceUnavailable(LambdaFWException):
    """503 - The server cannot process the request due to a high load"""

    message = HTTPStatus.SERVICE_UNAVAILABLE.description
    status_code = HTTPStatus.SERVICE_UNAVAILABLE.value


class GatewayTimeout(LambdaFWException):
    """504 - The gateway server did not receive a timely response"""

    message = HTTPStatus.GATEWAY_TIMEOUT.description
    status_code = HTTPStatus.GATEWAY_TIMEOUT.value


class HTTPVersionNotSupported(LambdaFWException):
    """505 - Cannot fulfill request"""

    message = HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.description
    status_code = HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.value


class VariantAlsoNegotiates(LambdaFWException):
    """506 -"""

    message = HTTPStatus.VARIANT_ALSO_NEGOTIATES.description
    status_code = HTTPStatus.VARIANT_ALSO_NEGOTIATES.value


class InsufficientStorage(LambdaFWException):
    """507 -"""

    message = HTTPStatus.INSUFFICIENT_STORAGE.description
    status_code = HTTPStatus.INSUFFICIENT_STORAGE.value


class LoopDetected(LambdaFWException):
    """508 -"""

    message = HTTPStatus.LOOP_DETECTED.description
    status_code = HTTPStatus.LOOP_DETECTED.value


class NotExtended(LambdaFWException):
    """510 -"""

    message = HTTPStatus.NOT_EXTENDED.description
    status_code = HTTPStatus.NOT_EXTENDED.value


class NetworkAuthenticationRequired(LambdaFWException):
    """511 - The client needs to authenticate to gain network access"""

    message = HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.description
    status_code = HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.value
