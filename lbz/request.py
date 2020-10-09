#!/usr/local/bin/python3.8
# coding=utf-8
"""
Communication Helpers
"""
import base64
import json
import logging

from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict


class Request:
    """
    Represent request from API gateway.
    """

    _json_body = None
    _raw_body = b""

    def __init__(
        self,
        headers: dict,
        uri_params: dict,
        method: str,
        body: str,
        context: dict,
        stage_vars: dict,
        is_base64_encoded: bool,
        query_params: dict = None,
        user: dict = None,
    ):
        self.query_params = MultiDict(query_params)
        self.headers = headers
        self.uri_params = uri_params
        self.method = method
        self.context = context
        self.stage_vars = stage_vars
        self.user = user
        self._is_base64_encoded = is_base64_encoded
        self._body = body

    def __repr__(self):
        return f"<Request {self.method} >"

    @staticmethod
    def _decode_base64(encoded):
        if not isinstance(encoded, bytes):
            encoded = encoded.encode("ascii")
        output = base64.b64decode(encoded)
        return output

    @property
    def raw_body(self):
        if not self._raw_body and self._body is not None:
            if self._is_base64_encoded:
                self._raw_body = self._decode_base64(self._body)
            elif not isinstance(self._body, bytes):
                self._raw_body = self._body.encode("utf-8")
            else:
                self._raw_body = self._body
        return self._raw_body

    @property
    def json_body(self):
        content_type = self.headers.get("Content-Type", self.headers.get("content-type"))
        if content_type is None:
            return
        if content_type.startswith("application/json"):
            if isinstance(self._body, dict):
                return self._body
            if self._json_body is None:
                try:
                    self._json_body = json.loads(self.raw_body)
                except ValueError:
                    logging.error(f"Error during deserialization: {self.raw_body}")
                    raise BadRequestError()
            return self._json_body
        else:
            logging.error(self)
            logging.exception("Wrong Header %s", json.dumps(self.headers))
            c_header = json.dumps(self.headers.get("Content-Type", ""))
            raise BadRequestError(f"Content-Type header is missing or wrong: {c_header}")

    def to_dict(self):
        copied = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        copied["headers"] = dict(copied["headers"])
        copied["user"] = repr(copied["user"])
        if copied["query_params"] is not None:
            copied["query_params"] = dict(copied["query_params"])
        return copied
