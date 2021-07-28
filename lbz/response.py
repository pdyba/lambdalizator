# coding=utf-8
"""
Standardised response module.
"""
import json
from typing import Union


class Response:
    """Response from lambda.

    Performs automatic dumping when body is dict. Otherwise payload just passes through."""

    def __init__(
        self,
        body: Union[str, dict],
        /,
        headers: dict = None,
        status_code: int = 200,
        base64_encoded: bool = False,
    ):
        self.body = body
        self.is_json = isinstance(body, dict)
        self.headers = headers if headers is not None else self.get_content_header()
        self.status_code = status_code
        self.is_base64 = base64_encoded

    def get_content_header(self) -> dict:
        """
        Adds necessary headers based on content type
        """
        if self.is_json:
            return {"Content-Type": "application/json"}
        if isinstance(self.body, str):
            return {"Content-Type": "text/plain"}
        raise RuntimeError("Response body type not supported yet.")

    def to_dict(self) -> dict:
        """
        Dumps response to AWS Lambda compatible response format.
        """
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
