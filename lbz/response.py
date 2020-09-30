#!/usr/local/bin/python3.8
# coding=utf-8
"""
Communication Helpers
"""
import base64
import json


class Response:
    """
    Response from lambda.
    """

    def __init__(self, body, /, headers: dict = None, status_code: int = 200):
        self.body = body if isinstance(body, dict) else {"message": body}
        self.headers = (
            {"Content-Type": "application/json"} if headers is None else headers
        )
        self.status_code = status_code
        self.base64 = False

    def to_dict(self, binary_types=None):
        if binary_types is not None:
            self.base64 = True
            body = self._encode_base64(self.body)
        else:
            body = json.dumps(self.body, separators=(",", ":"))
        response = {
            "headers": self.headers,
            "statusCode": int(self.status_code),
            "body": body,
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
