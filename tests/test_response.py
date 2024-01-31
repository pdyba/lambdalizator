# coding=utf-8
from base64 import b64encode
from typing import Any

import pytest

from lbz.exceptions import LambdaFWException, ServerError
from lbz.response import Response


class TestResponseInit:
    def test___init__(self) -> None:
        resp = Response({})
        assert isinstance(resp.body, dict)
        assert resp.headers == {"Content-Type": "application/json"}
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
            "headers": {"Content-Type": "application/json"},
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
            "headers": {"Content-Type": "application/json"},
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
            "headers": {"Content-Type": "application/json"},
            "isBase64Encoded": False,
            "statusCode": 500,
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

    def test__json__raises_value_error_when_body_is_not_a_string(self) -> None:
        response = Response("")
        response.body = []  # type: ignore

        with pytest.raises(ValueError, match="Got unexpected type to decode <class 'list'>"):
            assert response.json()

    @pytest.mark.parametrize(
        "body, headers, is_json",
        [
            ({"message": "It is alive!"}, {}, True),
            ('{"message":"It is alive!"}', {"Content-Type": "application/json"}, True),
            ('{"message":"It is alive!"}', {"Content-Type": "text/plain"}, False),
            ('{"message":"It is alive!"}', {}, False),
            ("", {}, False),
        ],
    )
    def test__is_json__returns_bool_based_on_declared_body_and_headers(
        self, body: Any, headers: dict, is_json: bool
    ) -> None:
        response = Response(body, headers=headers)

        assert response.is_json == is_json
