from __future__ import annotations

from collections.abc import Generator
from http import HTTPStatus
from typing import Any

from lbz.response import Response


class SecurityError(Exception):
    """Request did not match security requirements expected by server."""


class MissingConfigValue(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(f"'{key}' was not defined.")


class ConfigValueParsingFailed(Exception):
    def __init__(self, key: str, value: Any) -> None:
        super().__init__(f"'{key}' could not parse '{value}'")


class LambdaFWException(Exception):
    """Standardised for AWS Lambda exception class."""

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code: str | None = None

    def __init__(self, message: str = "", error_code: str | None = None) -> None:
        super().__init__(message)
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"[{self.status_code}] {self.error_code} - {self.message}"
        return f"[{self.status_code}] {self.message}"

    def get_response(self, request_id: str) -> Response:
        """Creates a proper standardised Response for Errors."""
        resp_data = {"message": self.message, "request_id": request_id}
        if self.error_code:
            resp_data["error_code"] = self.error_code

        return Response(resp_data, status_code=self.status_code)


class LambdaFWClientException(LambdaFWException):
    """400 - 499 Exceptions for easier distinguishably when developing"""


class LambdaFWServerException(LambdaFWException):
    """500 - 599 Exceptions for easier distinguishably when developing"""


class BadRequestError(LambdaFWClientException):
    """400 - Bad request syntax or unsupported method"""

    message = HTTPStatus.BAD_REQUEST.description
    status_code = HTTPStatus.BAD_REQUEST.value


class InvalidResolutionError(LambdaFWClientException):
    """400 - Unaccepted image resolution"""

    message = "Unaccepted image resolution"
    status_code = HTTPStatus.BAD_REQUEST.value


class Unauthorized(LambdaFWClientException):
    """401 - No permission -- see authorization schemes"""

    message = HTTPStatus.UNAUTHORIZED.description
    status_code = HTTPStatus.UNAUTHORIZED.value


class PaymentRequired(LambdaFWClientException):
    """402 - No payment -- see charging schemes"""

    message = HTTPStatus.PAYMENT_REQUIRED.description
    status_code = HTTPStatus.PAYMENT_REQUIRED.value


class PermissionDenied(LambdaFWClientException):
    """403 - Request forbidden -- authorization will not help"""

    message = HTTPStatus.FORBIDDEN.description
    status_code = HTTPStatus.FORBIDDEN.value


class NotFound(LambdaFWClientException):
    """404 - Nothing matches the given URI"""

    message = HTTPStatus.NOT_FOUND.description
    status_code = HTTPStatus.NOT_FOUND.value


class UnsupportedMethod(LambdaFWClientException):
    """405 - Unsupported method: <method>"""

    status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    def __init__(self, method: str) -> None:
        super().__init__(message=f"Unsupported method: {method}")


class NotAcceptable(LambdaFWClientException):
    """406 - URI not available in preferred format"""

    message = HTTPStatus.NOT_ACCEPTABLE.description
    status_code = HTTPStatus.NOT_ACCEPTABLE.value


class ProxyAuthenticationRequired(LambdaFWClientException):
    """407 - You must authenticate with this proxy before proceeding"""

    message = HTTPStatus.PROXY_AUTHENTICATION_REQUIRED.description
    status_code = HTTPStatus.PROXY_AUTHENTICATION_REQUIRED.value


class RequestTimeout(LambdaFWClientException):
    """408 - Request timed out; try again later"""

    message = HTTPStatus.REQUEST_TIMEOUT.description
    status_code = HTTPStatus.REQUEST_TIMEOUT.value


class Conflict(LambdaFWClientException):
    """409 - Request conflict"""

    message = HTTPStatus.CONFLICT.description
    status_code = HTTPStatus.CONFLICT.value


class Gone(LambdaFWClientException):
    """410 - URI no longer exists and has been permanently removed"""

    message = HTTPStatus.GONE.description
    status_code = HTTPStatus.GONE.value


class LengthRequired(LambdaFWClientException):
    """411 - Client must specify Content-Length"""

    message = HTTPStatus.LENGTH_REQUIRED.description
    status_code = HTTPStatus.LENGTH_REQUIRED.value


class PreconditionFailed(LambdaFWClientException):
    """412 - Precondition in headers is false"""

    message = HTTPStatus.PRECONDITION_FAILED.description
    status_code = HTTPStatus.PRECONDITION_FAILED.value


class PayloadTooLarge(LambdaFWClientException):
    """413 - Entity is too large"""

    message = HTTPStatus.REQUEST_ENTITY_TOO_LARGE.description
    status_code = HTTPStatus.REQUEST_ENTITY_TOO_LARGE.value


class URITooLong(LambdaFWClientException):
    """414 - URI is too long"""

    message = HTTPStatus.REQUEST_URI_TOO_LONG.description
    status_code = HTTPStatus.REQUEST_URI_TOO_LONG.value


class UnsupportedMediaType(LambdaFWClientException):
    """415 - Entity body in unsupported format"""

    message = HTTPStatus.UNSUPPORTED_MEDIA_TYPE.description
    status_code = HTTPStatus.UNSUPPORTED_MEDIA_TYPE.value


class RangeNotSatisfiable(LambdaFWClientException):
    """416 - Cannot satisfy request range"""

    message = HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE.description
    status_code = HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE.value


class ExpectationFailed(LambdaFWClientException):
    """417 - Expect condition could not be satisfied"""

    message = HTTPStatus.EXPECTATION_FAILED.description
    status_code = HTTPStatus.EXPECTATION_FAILED.value


class ImATeapot(LambdaFWClientException):
    """418 - The server refuses the attempt to brew coffee with a teapot"""

    message = "The server refuses the attempt to brew coffee with a teapot"
    status_code = 418


class MisdirectedRequest(LambdaFWClientException):
    """421 - Server is not able to produce a response"""

    message = HTTPStatus.MISDIRECTED_REQUEST.description
    status_code = HTTPStatus.MISDIRECTED_REQUEST.value


class UnprocessableEntity(LambdaFWClientException):
    """422 -"""

    message = HTTPStatus.UNPROCESSABLE_ENTITY.description
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value


class Locked(LambdaFWClientException):
    """423 -"""

    message = HTTPStatus.LOCKED.description
    status_code = HTTPStatus.LOCKED.value


class FailedDependency(LambdaFWClientException):
    """424 -"""

    message = HTTPStatus.FAILED_DEPENDENCY.description
    status_code = HTTPStatus.FAILED_DEPENDENCY.value


class TooEarly(LambdaFWClientException):
    """425 - Server is not ready to process request try again later"""

    message = "Server is not ready to process request try again later"
    status_code = 425


class UpgradeRequired(LambdaFWClientException):
    """426 -"""

    message = HTTPStatus.UPGRADE_REQUIRED.description
    status_code = HTTPStatus.UPGRADE_REQUIRED.value


class PreconditionRequired(LambdaFWClientException):
    """428 - The origin server requires the request to be conditional"""

    message = HTTPStatus.PRECONDITION_REQUIRED.description
    status_code = HTTPStatus.PRECONDITION_REQUIRED.value


class TooManyRequests(LambdaFWClientException):
    """429 - The user has sent too many requests in a given amount of time ("rate limiting")"""

    message = HTTPStatus.TOO_MANY_REQUESTS.description
    status_code = HTTPStatus.TOO_MANY_REQUESTS.value


class RequestHeaderFieldsTooLarge(LambdaFWClientException):
    """431 - The server is unwilling to process the request because its header fields are too large"""  # noqa: E501

    message = HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE.description
    status_code = HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE.value


class UnavailableForLegalReasons(LambdaFWClientException):
    """451 - The server is denying access to the resource as a consequence of a legal demand"""

    message = HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS.description
    status_code = HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS.value


class ServerError(LambdaFWServerException):
    """500 - Server got itself in trouble"""

    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value


class NotImplementedFunctionality(LambdaFWServerException):
    """501 - Server does not support this operation"""

    message = HTTPStatus.NOT_IMPLEMENTED.description
    status_code = HTTPStatus.NOT_IMPLEMENTED.value


class BadGateway(LambdaFWServerException):
    """502 - Invalid responses from another server/proxy"""

    message = HTTPStatus.BAD_GATEWAY.description
    status_code = HTTPStatus.BAD_GATEWAY.value


class ServiceUnavailable(LambdaFWServerException):
    """503 - The server cannot process the request due to a high load"""

    message = HTTPStatus.SERVICE_UNAVAILABLE.description
    status_code = HTTPStatus.SERVICE_UNAVAILABLE.value


class GatewayTimeout(LambdaFWServerException):
    """504 - The gateway server did not receive a timely response"""

    message = HTTPStatus.GATEWAY_TIMEOUT.description
    status_code = HTTPStatus.GATEWAY_TIMEOUT.value


class HTTPVersionNotSupported(LambdaFWServerException):
    """505 - Cannot fulfill request"""

    message = HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.description
    status_code = HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.value


class VariantAlsoNegotiates(LambdaFWServerException):
    """506 -"""

    message = HTTPStatus.VARIANT_ALSO_NEGOTIATES.description
    status_code = HTTPStatus.VARIANT_ALSO_NEGOTIATES.value


class InsufficientStorage(LambdaFWServerException):
    """507 -"""

    message = HTTPStatus.INSUFFICIENT_STORAGE.description
    status_code = HTTPStatus.INSUFFICIENT_STORAGE.value


class LoopDetected(LambdaFWServerException):
    """508 -"""

    message = HTTPStatus.LOOP_DETECTED.description
    status_code = HTTPStatus.LOOP_DETECTED.value


class NotExtended(LambdaFWServerException):
    """510 -"""

    message = HTTPStatus.NOT_EXTENDED.description
    status_code = HTTPStatus.NOT_EXTENDED.value


class NetworkAuthenticationRequired(LambdaFWServerException):
    """511 - The client needs to authenticate to gain network access"""

    message = HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.description
    status_code = HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.value


def all_lbz_errors(
    cls: type[LambdaFWException] = LambdaFWException,
) -> Generator[type[LambdaFWException], None, None]:
    for subcls in cls.__subclasses__():
        if subcls not in [LambdaFWClientException, LambdaFWServerException]:
            yield subcls
        yield from all_lbz_errors(subcls)
