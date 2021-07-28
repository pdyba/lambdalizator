# coding=utf-8
"""
Request standardisation module.
"""
import base64
import json
from typing import Optional, Union

from multidict import CIMultiDict

from lbz.authentication import User
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict, get_logger

logger = get_logger(__name__)


class Request:
    """Represents request from API gateway."""

    _json_body: dict = {}
    _raw_body = b""

    def __init__(
        self,
        headers: CIMultiDict,
        uri_params: dict,
        method: str,
        body: str,
        context: dict,
        stage_vars: dict,
        is_base64_encoded: bool,
        query_params: dict = None,
        user: User = None,
    ):
        self.query_params: MultiDict = MultiDict(query_params or {})
        self.headers: CIMultiDict = headers
        self.uri_params: dict = uri_params
        self.method: str = method
        self.context: dict = context
        self.stage_vars = stage_vars
        self.user: Optional[User] = user
        self._is_base64_encoded: bool = is_base64_encoded
        self._body: Union[str, bytes] = body

    def __repr__(self) -> str:
        return f"<Request {self.method} >"

    @staticmethod
    def _decode_base64(encoded: Union[str, bytes]) -> bytes:
        if not isinstance(encoded, bytes):
            encoded = encoded.encode("ascii")
        return base64.b64decode(encoded)

    @property
    def raw_body(self) -> Union[bytes, str]:
        if not self._raw_body and self._body is not None:
            if self._is_base64_encoded:
                self._raw_body = self._decode_base64(self._body)
            elif not isinstance(self._body, bytes):
                self._raw_body = self._body.encode("utf-8")
            else:
                self._raw_body = self._body
        return self._raw_body

    @property
    def json_body(self) -> Optional[dict]:
        content_type = self.headers.get("Content-Type")
        if content_type is None:
            return None
        if content_type.startswith("application/json"):
            if not self._json_body:
                try:
                    self._json_body = json.loads(self.raw_body)
                except ValueError as error:
                    raise BadRequestError(
                        "Payload is invalid.\nPayload body:\n {!r}".format(self.raw_body)
                    ) from error
            return self._json_body
        logger.warning("Wrong headers: %s", self.headers)
        raise BadRequestError(f"Content-Type header is missing or wrong: {content_type}")

    def to_dict(self) -> dict:
        copied = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        copied["headers"] = dict(copied["headers"])
        copied["user"] = repr(copied["user"])
        if copied["query_params"] is not None:
            copied["query_params"] = dict(copied["query_params"])
        return copied
