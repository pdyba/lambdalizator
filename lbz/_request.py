from __future__ import annotations

import base64
import json
from typing import Any

from lbz.exceptions import BadRequestError


class Request:
    def __init__(
        self,
        body: str | bytes | dict,
        is_base64_encoded: bool,
    ) -> None:
        self._is_base64_encoded = is_base64_encoded
        self._body = body
        self._json_body: dict | None = None
        self._raw_body: bytes | dict | None = None

    @property
    def raw_body(self) -> bytes | dict | None:
        if self._raw_body is None and self._body is not None:
            if self._is_base64_encoded and isinstance(self._body, (bytes, str)):
                self._raw_body = self._decode_base64(self._body)
            elif isinstance(self._body, str):
                self._raw_body = self._body.encode("utf-8")
            else:
                self._raw_body = self._body
        return self._raw_body

    @staticmethod
    def _decode_base64(encoded: str | bytes) -> bytes:
        if not isinstance(encoded, bytes):
            encoded = encoded.encode("ascii")
        return base64.b64decode(encoded)

    @staticmethod
    def _safe_json_loads(payload: str | bytes) -> Any:
        try:
            return json.loads(payload)
        except ValueError as error:
            raise BadRequestError(f"Invalid payload.\nPayload body:\n {repr(payload)}") from error
