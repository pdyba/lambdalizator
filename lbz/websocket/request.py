from __future__ import annotations

from multidict import CIMultiDict

from lbz._request import _Request
from lbz.authentication import User
from lbz.misc import get_logger
from lbz.websocket.enums import ActionType

logger = get_logger(__name__)


class WebSocketRequest(_Request):
    """Represents request from Web Socket Secure API Gateway.

    rel: https://docs.aws.amazon.com/apigateway/latest/developerguide/
    apigateway-websocket-api-mapping-template-reference.html
    """

    def __init__(
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

    @property
    def json_body(self) -> dict | None:
        if self._json_body is None:
            if isinstance(self.raw_body, dict) or self.raw_body is None:
                self._json_body = self.raw_body
            else:
                self._json_body = self._safe_json_loads(self.raw_body)
        return self._json_body

    def is_connection_request(self) -> bool:
        return self.action_type is ActionType.CONNECT

    def is_disconnection_request(self) -> bool:
        return self.action_type is ActionType.DISCONNECT
