#!/usr/local/bin/python3.8
# coding=utf-8
import base64
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
        if self.is_json:
            return {"Content-Type": "application/json"}
        elif isinstance(self.body, str):
            return {"Content-Type": "text/plain"}
        raise RuntimeError("Response body type not supported yet.")

    def to_dict(self):
        body = json.dumps(self.body, separators=(",", ":")) if self.is_json else self.body
        response = {
            "headers": self.headers,
            "statusCode": self.status_code,
            "body": body,
            "isBase64Encoded": self.is_base64,
        }

        return response

    @staticmethod
    def _encode_base64(data):
        if not isinstance(data, bytes):
            raise ValueError(
                "Expected bytes type for body with binary "
                "Content-Type. Got %s type body instead." % type(data)
            )
        data = base64.b64encode(data)
        return data.decode("ascii")
