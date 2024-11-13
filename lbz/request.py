from __future__ import annotations

import base64
import json
from typing import Any

from multidict import CIMultiDict

from lbz.authentication import User
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict, get_logger
from lbz.rest import ContentType
from lbz.websocket import ActionType

logger = get_logger(__name__)


class BaseRequest:
    def __init__(
        self,
        body: str | bytes | dict,
        is_base64_encoded: bool,
    ):
        self._is_base64_encoded = is_base64_encoded
        self._body = body
        self._json_body: dict | None = None
        self._raw_body: bytes | dict | None = None

    @staticmethod
    def _decode_base64(encoded: str | bytes) -> bytes:
        if not isinstance(encoded, bytes):
            encoded = encoded.encode("ascii")
        return base64.b64decode(encoded)

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
    def _safe_json_loads(payload: str | bytes) -> Any:
        try:
            return json.loads(payload)
        except ValueError as error:
            raise BadRequestError(f"Invalid payload.\nPayload body:\n {repr(payload)}") from error


class Request(BaseRequest):
    """Represents request from HTTP API Gateway."""

    def __init__(
        # pylint: disable=too-many-positional-arguments
        self,
        headers: CIMultiDict,
        uri_params: dict,
        method: str,
        body: str | bytes | dict,
        context: dict,
        stage_vars: dict,
        is_base64_encoded: bool,
        query_params: dict | None = None,
        user: User | None = None,
    ):
        self.query_params = MultiDict(query_params or {})
        self.headers = headers
        self.uri_params = uri_params
        self.method = method
        self.context = context
        self.stage_vars = stage_vars
        self.user = user
        super().__init__(body=body, is_base64_encoded=is_base64_encoded)

    def __repr__(self) -> str:
        return f"<Request {self.method} >"

    def to_dict(self) -> dict:
        copied = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        copied["headers"] = dict(copied["headers"])
        copied["user"] = repr(copied["user"])
        if copied["query_params"] is not None:
            copied["query_params"] = dict(copied["query_params"])
        return copied

    @property
    def json_body(self) -> dict | None:
        if self._json_body is None:
            content_type: str | None = self.headers.get("Content-Type")
            if content_type is None:  # pylint: disable=consider-using-assignment-expr
                return None
            if content_type.startswith(ContentType.JSON):
                if isinstance(self.raw_body, dict) or self.raw_body is None:
                    self._json_body = self.raw_body
                else:
                    self._json_body = self._safe_json_loads(self.raw_body)
            else:
                logger.warning("Wrong headers: %s", self.headers)
                raise BadRequestError(f"Content-Type header is missing or wrong: {content_type}")
        return self._json_body


class WebSocketRequest(BaseRequest):
    """Represents request from Web Socket Secure API Gateway."""

    def __init__(
        # pylint: disable=too-many-positional-arguments
        self,
        body: str | bytes | dict,
        request_details: dict,
        context: dict,
        is_base64_encoded: bool,
        user: User | None = None,
        headers: CIMultiDict | None = None,
    ):
        self.headers = headers
        self.context = context
        self.user = user
        self.action = request_details.pop("routeKey")
        self.action_type = request_details.pop("eventType")
        self.connection_id = request_details.pop("connectionId")
        self.domain = request_details.pop("domainName")
        self.stage = request_details.pop("stage")
        self.details = request_details
        super().__init__(body=body, is_base64_encoded=is_base64_encoded)

    def __repr__(self) -> str:
        return f"<Request {self.action_type} - {self.action} >"

    def is_connection_request(self) -> bool:
        return self.action_type is ActionType.CONNECT

    def is_disconnection_request(self) -> bool:
        return self.action_type is ActionType.DISCONNECT

    @property
    def json_body(self) -> dict | None:
        if self._json_body is None:
            if isinstance(self.raw_body, dict) or self.raw_body is None:
                self._json_body = self.raw_body
            else:
                self._json_body = self._safe_json_loads(self.raw_body)
        return self._json_body


HTTPRequest = Request
