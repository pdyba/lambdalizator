from __future__ import annotations

import json

from lbz.exceptions import LambdaFWException
from lbz.misc import deprecated
from lbz.rest import ContentType


class Response:
    """Response from lambda.

    Performs automatic dumping when body is dict, otherwise payload just passes through.
    """

    def __init__(
        self,
        body: str | dict,
        /,
        headers: dict | None = None,
        status_code: int = 200,
        base64_encoded: bool = False,
    ):
        self.body = body
        self._json = body if isinstance(body, dict) else None
        self.headers = headers if headers is not None else self._get_content_header()
        self.status_code = status_code
        # TODO: handle bae64 encoded responses appropriately
        self.is_base64 = base64_encoded

    def __repr__(self) -> str:
        return f"<Response(status_code={self.status_code})>"

    @classmethod
    def from_exception(cls, error: LambdaFWException, request_id: str) -> Response:
        """Creates a proper standardised Response for Errors."""
        resp_data = {"message": error.message, "request_id": request_id}
        if error.error_code:
            resp_data["error_code"] = error.error_code

        return cls(resp_data, status_code=error.status_code)

    @property
    def is_json(self) -> bool:
        if isinstance(self.body, dict):
            return True
        if self.headers.get("Content-Type", "").startswith(ContentType.JSON):
            return True
        return False

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    def to_dict(self) -> dict:
        """Dumps response to AWS Lambda compatible response format."""
        body = (
            json.dumps(self.body, separators=(",", ":"), default=str)
            if self.is_json
            else self.body
        )
        response = {
            "headers": self.headers,
            "statusCode": self.status_code,
            "body": body,
            "isBase64Encoded": self.is_base64,
        }

        return response

    def json(self) -> dict:
        if self._json is None:
            self._json = json.loads(self.body)  # type: ignore[arg-type]
        return self._json

    @deprecated(message="Use the ok property instead", version="0.7.0")
    def is_ok(self) -> bool:
        return self.ok

    def _get_content_header(self) -> dict:
        """Adds necessary headers based on content type"""
        if isinstance(self.body, dict):
            return {"Content-Type": ContentType.JSON}
        if isinstance(self.body, str):
            return {"Content-Type": ContentType.TEXT}
        raise RuntimeError("Response body type not supported yet.")
