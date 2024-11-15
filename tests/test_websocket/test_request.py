import pytest

from lbz.websocket import ActionType, WebSocketRequest


class TestWebSocketRequest:
    def test__decode_base64_bytes(self) -> None:
        encoded = b"asdasdsd"
        output = WebSocketRequest._decode_base64(encoded)  # pylint: disable=protected-access
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test__decode_base64_str(self) -> None:
        encoded = "asdasdsd"
        output = WebSocketRequest._decode_base64(encoded)  # pylint: disable=protected-access
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    @pytest.mark.parametrize(
        "action_type, is_connection_req",
        [
            (ActionType.CONNECT, True),
            (ActionType.DISCONNECT, False),
            (ActionType.MESSAGE, False),
        ],
    )
    def test__is_connection_request__checks_if_request_was_a_connection_request(
        self, action_type: str, is_connection_req: bool
    ) -> None:
        request = WebSocketRequest(
            body="",
            request_details={
                "routeKey": "$connect",
                "eventType": action_type,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            context={},
            is_base64_encoded=False,
        )

        assert request.is_connection_request() == is_connection_req

    @pytest.mark.parametrize(
        "action_type, is_connection_req",
        [
            (ActionType.CONNECT, False),
            (ActionType.DISCONNECT, True),
            (ActionType.MESSAGE, False),
        ],
    )
    def test__is_disconnection_request__checks_if_request_was_a_disconnection_request(
        self, action_type: str, is_connection_req: bool
    ) -> None:
        request = WebSocketRequest(
            body="",
            request_details={
                "routeKey": "$connect",
                "eventType": action_type,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            context={},
            is_base64_encoded=False,
        )

        assert request.is_disconnection_request() == is_connection_req

    def test__json_body__returns_dict_when_body_is_a_dict(self) -> None:
        request = WebSocketRequest(
            body={"x": "t1"},
            request_details={
                "routeKey": "$connect",
                "eventType": ActionType.MESSAGE,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            context={},
            is_base64_encoded=False,
        )
        assert request.json_body == {"x": "t1"}

    def test__json_body___returns_dict_when_body_is_a_str(self) -> None:
        request = WebSocketRequest(
            body='{"x": "t1"}',
            request_details={
                "routeKey": "$connect",
                "eventType": ActionType.MESSAGE,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            context={},
            is_base64_encoded=False,
        )
        assert request.json_body == {"x": "t1"}
