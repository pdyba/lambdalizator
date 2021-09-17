# coding=utf-8
"""
Request standardisation module.
"""
import base64
import json
from typing import Optional, Union, Any

from multidict import CIMultiDict

from lbz.authentication import User
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict, get_logger

logger = get_logger(__name__)


class Request:
    """Represents request from API gateway."""

    def __init__(
        self,
        headers: CIMultiDict,
        uri_params: dict,
        method: str,
        body: Union[str, bytes, dict],
        context: dict,
        stage_vars: dict,
        is_base64_encoded: bool,
        query_params: Optional[dict] = None,
        user: Optional[User] = None,
    ):
        self.query_params = MultiDict(query_params or {})
        self.headers = headers
        self.uri_params = uri_params
        self.method = method
        self.context = context
        self.stage_vars = stage_vars
        self.user = user
        self._is_base64_encoded = is_base64_encoded
        self._body = body
        self._json_body: Optional[dict] = None
        self._raw_body: Optional[Union[bytes, dict]] = None

    def __repr__(self) -> str:
        return f"<Request {self.method} >"

    @staticmethod
    def _decode_base64(encoded: Union[str, bytes]) -> bytes:
        if not isinstance(encoded, bytes):
            encoded = encoded.encode("ascii")
        return base64.b64decode(encoded)

    @property
    def raw_body(self) -> Optional[Union[bytes, dict]]:
        if self._raw_body is None and self._body is not None:
            if self._is_base64_encoded and isinstance(self._body, (bytes, str)):
                self._raw_body = self._decode_base64(self._body)
            elif isinstance(self._body, str):
                self._raw_body = self._body.encode("utf-8")
            else:
                self._raw_body = self._body
        return self._raw_body

    @staticmethod
    def _safe_json_loads(payload: Union[str, bytes]) -> Optional[Any]:
        try:
            return json.loads(payload)
        except ValueError as error:
            raise BadRequestError(
                "Invalid payload.\nPayload body:\n {!r}".format(payload)
            ) from error

    @property
    def json_body(self) -> Optional[dict]:
        if self._json_body is None:
            content_type = self.headers.get("Content-Type")
            if content_type is None:
                return None
            if content_type.startswith("application/json"):
                if isinstance(self.raw_body, dict) or self.raw_body is None:
                    self._json_body = self.raw_body
                else:
                    self._json_body = self._safe_json_loads(self.raw_body)
            else:
                logger.warning("Wrong headers: %s", self.headers)
                raise BadRequestError(f"Content-Type header is missing or wrong: {content_type}")
        return self._json_body

    def to_dict(self) -> dict:
        copied = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        copied["headers"] = dict(copied["headers"])
        copied["user"] = repr(copied["user"])
        if copied["query_params"] is not None:
            copied["query_params"] = dict(copied["query_params"])
        return copied
