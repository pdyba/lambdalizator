# coding=utf-8

import pytest
from multidict import CIMultiDict

from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict
from lbz.request import BaseRequest, HTTPRequest, WebSocketRequest
from lbz.rest import ContentType
from lbz.websocket import ActionType


class TestBaseRequest:
    def test__decode_base64_bytes(self) -> None:
        encoded = b"asdasdsd"
        output = BaseRequest._decode_base64(encoded)  # pylint: disable=protected-access
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test__decode_base64_str(self) -> None:
        encoded = "asdasdsd"
        output = BaseRequest._decode_base64(encoded)  # pylint: disable=protected-access
        assert output == b"j\xc7Z\xb1\xdb\x1d"


class TestHTTPRequest:
    def test__init__(self) -> None:
        req = HTTPRequest(
            uri_params={},
            method="",
            body="",
            context={},
            headers=CIMultiDict(),  # pylint issue #214
            stage_vars={},
            query_params=None,
            is_base64_encoded=False,
            user=None,
        )
        assert isinstance(req.query_params, MultiDict)
        assert isinstance(req.headers, CIMultiDict)
        assert isinstance(req.uri_params, dict)
        assert isinstance(req.uri_params, dict)
        assert isinstance(req.context, dict)
        assert isinstance(req.stage_vars, dict)
        assert isinstance(req.method, str)
        assert isinstance(req._body, str)  # pylint: disable=protected-access
        assert isinstance(req._is_base64_encoded, bool)  # pylint: disable=protected-access
        assert req.user is None

    def test___repr__(self, sample_request: HTTPRequest) -> None:
        assert str(sample_request) == f"<Request {sample_request.method} >"

    def test_raw_body_base64_bytes(self, sample_request: HTTPRequest) -> None:
        sample_request._body = b"asdasdsd"  # pylint: disable=protected-access
        sample_request._is_base64_encoded = True  # pylint: disable=protected-access
        assert sample_request.raw_body == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_base64_str(self, sample_request: HTTPRequest) -> None:
        sample_request._body = "asdasdsd"  # pylint: disable=protected-access
        sample_request._is_base64_encoded = True  # pylint: disable=protected-access
        assert sample_request.raw_body == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_bytes(self, sample_request: HTTPRequest) -> None:
        sample_request._body = b"asdasdsd"  # pylint: disable=protected-access
        assert sample_request.raw_body == b"asdasdsd"

    def test_raw_body_str(self, sample_request: HTTPRequest) -> None:
        sample_request._body = "abcx"  # pylint: disable=protected-access
        assert sample_request.raw_body == b"abcx"

    def test_accessing_user_attributes(self, sample_request_with_user: HTTPRequest) -> None:
        assert isinstance(sample_request_with_user.user.username, str)  # type: ignore
        assert isinstance(sample_request_with_user.user.email, str)  # type: ignore
        for custom_param in range(1, 5):
            assert isinstance(getattr(sample_request_with_user.user, str(custom_param)), str)

    def test_headers_are_case_insensitive(self, sample_request_with_user: HTTPRequest) -> None:
        assert sample_request_with_user.headers["content-type"] == ContentType.JSON
        assert sample_request_with_user.headers["CoNtEnT-TyPe"] == ContentType.JSON

    def test_json_body_dict(self, sample_request: HTTPRequest) -> None:
        sample_request._body = {"x": "t1"}  # pylint: disable=protected-access
        assert sample_request.json_body == {"x": "t1"}

    def test_json_body_json(self, sample_request: HTTPRequest) -> None:
        sample_request._json_body = None  # pylint: disable=protected-access
        sample_request._body = '{"x": "t2"}'  # pylint: disable=protected-access
        assert sample_request.json_body == {"x": "t2"}
        assert sample_request._json_body == {"x": "t2"}  # pylint: disable=protected-access

    def test_json_body_base64_json(self, sample_request: HTTPRequest) -> None:
        sample_request._is_base64_encoded = True  # pylint: disable=protected-access
        sample_request._body = b"eyJ4IjogImFiY3gifQ=="  # pylint: disable=protected-access
        assert sample_request.json_body == {"x": "abcx"}
        assert sample_request._json_body == {"x": "abcx"}  # pylint: disable=protected-access

    def test_json_body_bad_json(self, sample_request: HTTPRequest) -> None:
        sample_request._json_body = None  # pylint: disable=protected-access
        sample_request._body = '{"x": t4}'  # pylint: disable=protected-access
        with pytest.raises(BadRequestError):
            sample_request.json_body  # pylint: disable=pointless-statement

    def test_json_body_bad_content_type(self, sample_request: HTTPRequest) -> None:
        sample_request.headers = CIMultiDict({"Content-Type": "application/dzejson"})
        with pytest.raises(BadRequestError) as err:
            sample_request.json_body  # pylint: disable=pointless-statement
            assert err.value.message.startswith("Content-Type header is missing or wrong")

    def test_json_body_none_when_no_content_type(self, sample_request: HTTPRequest) -> None:
        sample_request.headers = CIMultiDict({})
        assert sample_request.json_body is None

    def test_json_body_none_as_body(self, sample_request: HTTPRequest) -> None:
        sample_request._body = None  # type: ignore # pylint: disable=protected-access
        assert sample_request.json_body is None

    def test_to_dict(self, sample_request_with_user: HTTPRequest) -> None:
        assert sample_request_with_user.to_dict() == {
            "context": {},
            "headers": {"Content-Type": ContentType.JSON},
            "method": "GET",
            "query_params": {},
            "stage_vars": {},
            "uri_params": {},
            "user": f"User username={sample_request_with_user.user.username}",  # type: ignore
        }


class TestWebSocketRequest:
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
            "",
            {
                "routeKey": "$connect",
                "eventType": action_type,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            {},
            False,
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
            "",
            {
                "routeKey": "$connect",
                "eventType": action_type,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            {},
            False,
        )

        assert request.is_disconnection_request() == is_connection_req

    def test_json_body_dict(self) -> None:
        request = WebSocketRequest(
            {"x": "t1"},
            {
                "routeKey": "$connect",
                "eventType": ActionType.MESSAGE,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            {},
            False,
        )
        assert request.json_body == {"x": "t1"}

    def test_json_body_json(self) -> None:
        request = WebSocketRequest(
            '{"x": "t1"}',
            {
                "routeKey": "$connect",
                "eventType": ActionType.MESSAGE,
                "connectionId": "aaa123",
                "domainName": "xxx.com",
                "stage": "prod",
            },
            {},
            False,
        )
        assert request.json_body == {"x": "t1"}
