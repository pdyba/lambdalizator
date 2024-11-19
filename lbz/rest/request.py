from __future__ import annotations

from multidict import CIMultiDict

from lbz._request import Request
from lbz.authentication import User
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict, get_logger
from lbz.rest.enums import ContentType

logger = get_logger(__name__)


class HTTPRequest(Request):
    """Represents request from HTTP API Gateway."""

    def __init__(
        self,
        *,
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
        super().__init__(
            body=body,
            is_base64_encoded=is_base64_encoded,
            context=context,
            user=user,
        )
        self.headers = headers
        self.query_params = MultiDict(query_params or {})
        self.uri_params = uri_params
        self.method = method
        self.context = context
        self.stage_vars = stage_vars

    def __repr__(self) -> str:
        return f"<Request {self.method} >"

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

    def to_dict(self) -> dict:
        copied = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        copied["headers"] = dict(copied["headers"])
        copied["user"] = repr(copied["user"])
        if copied["query_params"] is not None:
            copied["query_params"] = dict(copied["query_params"])
        return copied
