from __future__ import annotations

from base64 import b64encode
from typing import Any

import pytest

from lbz.exceptions import LambdaFWException, ServerError
from lbz.response import Response
from lbz.rest import ContentType


class TestResponseInit:
    def test___init__(self) -> None:
        resp = Response({})
        assert isinstance(resp.body, dict)
        assert resp.headers == {"Content-Type": ContentType.JSON}
        assert resp.status_code == 200
        assert not resp.is_base64

    def test___init__2(self) -> None:
        resp = Response({"message": "xxx"}, headers={"xx": "xx"}, status_code=666)
        assert isinstance(resp.body, dict)
        assert resp.body == {"message": "xxx"}
        assert resp.headers == {"xx": "xx"}
        assert resp.status_code == 666
        assert not resp.is_base64


class TestResponse:
    def test_response_body_is_json_dump_when_dict(self) -> None:
        response = Response({"message": "xxx"}, headers={"xx": "xx"}, status_code=666)
        assert response.to_dict() == {
            "body": '{"message":"xxx"}',
            "headers": {"xx": "xx"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_application_json_header_added_when_dict_without_headers(self) -> None:
        response = Response({"message": "xxx"}, status_code=666)
        assert response.to_dict() == {
            "body": '{"message":"xxx"}',
            "headers": {"Content-Type": ContentType.JSON},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_response_body_passes_through_when_string(self) -> None:
        response = Response("xxx", headers={"xx": "xx"}, status_code=666)
        assert response.to_dict() == {
            "body": "xxx",
            "headers": {"xx": "xx"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_text_plain_header_added_when_string_without_headers(self) -> None:
        response = Response("xxx", status_code=666)
        assert response.to_dict() == {
            "body": "xxx",
            "headers": {"Content-Type": "text/plain"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_response_body_passes_through_when_base64(self) -> None:
        data = b64encode(b"xxx").decode("utf-8")
        response = Response(data, headers={"xx": "xx"}, status_code=666, base64_encoded=True)
        assert response.to_dict() == {
            "body": data,
            "headers": {"xx": "xx"},
            "statusCode": 666,
            "isBase64Encoded": True,
        }

    @pytest.mark.parametrize(
        "code, outcome",
        [
            (100, True),
            (200, True),
            (201, True),
            (300, True),
            (399, True),
            (400, False),
            (404, False),
            (500, False),
            (501, False),
            (666, False),
        ],
    )
    def test__ok__returns_bool_result_based_on_status_code(self, code: int, outcome: bool) -> None:
        response = Response({"message": "xxx"}, headers={"xx": "xx"}, status_code=code)

        assert response.ok == outcome
        assert response.is_ok() == outcome

    def test__from_exception__builds_response_based_on_provided_internal_error(self) -> None:
        response = Response.from_exception(ServerError(), "req-id")

        assert response.to_dict() == {
            "body": '{"message":"Server got itself in trouble","request_id":"req-id"}',
            "headers": {"Content-Type": ContentType.JSON},
            "isBase64Encoded": False,
            "statusCode": 500,
        }

    def test__from_exception__adds_error_code_to_response_body_if_only_declared(self) -> None:
        class RandomException(LambdaFWException):
            error_code = "RAND001"

        response = Response.from_exception(RandomException(), "req-id")

        assert response.to_dict() == {
            "body": (
                '{"message":"Server got itself in trouble",'
                '"request_id":"req-id",'
                '"error_code":"RAND001"}'
            ),
            "headers": {"Content-Type": ContentType.JSON},
            "isBase64Encoded": False,
            "statusCode": 500,
        }

    def test__from_exception__adds_extra_data_to_response_body_if_only_declared(self) -> None:
        class RandomException(LambdaFWException):
            error_code = "RAND001"

        response = Response.from_exception(
            RandomException(extra={"added_data": "random"}), "req-id"
        )

        assert response.headers == {"Content-Type": ContentType.JSON}
        assert response.is_base64 is False
        assert response.status_code == 500
        assert response.body == {
            "added_data": "random",
            "message": "Server got itself in trouble",
            "request_id": "req-id",
            "error_code": "RAND001",
        }

    @pytest.mark.parametrize(
        "body",
        [
            {"message": "It is alive!"},
            '{"message":"It is alive!"}',
        ],
    )
    def test__json__returns_dict_based_on_declared_body(self, body: Any) -> None:
        response = Response(body)

        assert response.json() == {"message": "It is alive!"}

    @pytest.mark.parametrize(
        "body, headers, is_json",
        [
            ({"message": "It is alive!"}, {}, True),
            ({"message": "It is alive!"}, {"Content-Type": ContentType.JSON}, True),
            ({"message": "It is alive!"}, {"Content-Type": ContentType.TEXT}, True),
            ('{"message":"It is alive!"}', {"Content-Type": ContentType.JSON}, True),
            ('{"message":"It is alive!"}', {"Content-Type": ContentType.TEXT}, False),
            ('{"message":"It is alive!"}', {}, False),
            ("", {}, False),
        ],
    )
    def test__is_json__returns_bool_based_on_declared_body_and_headers(
        self, body: str | dict, headers: dict, is_json: bool
    ) -> None:
        response = Response(body, headers=headers)

        assert response.is_json == is_json
