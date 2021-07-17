#!/usr/local/bin/python3.8
# coding=utf-8
from base64 import b64encode

from lbz.response import Response


class TestResponseInit:
    def test___init__(self):
        resp = Response({})
        assert isinstance(resp.body, dict)
        assert resp.headers == {"Content-Type": "application/json"}
        assert resp.status_code == 200
        assert not resp.is_base64

    def test___init__2(self):
        resp = Response({"message": "xxx"}, headers={"xx": "xx"}, status_code=666)
        assert isinstance(resp.body, dict)
        assert resp.body == {"message": "xxx"}
        assert resp.headers == {"xx": "xx"}
        assert resp.status_code == 666
        assert not resp.is_base64


class TestResponse:
    def test_response_body_is_json_dump_when_dict(self):
        response = Response({"message": "xxx"}, headers={"xx": "xx"}, status_code=666)
        assert response.to_dict() == {
            "body": '{"message":"xxx"}',
            "headers": {"xx": "xx"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_application_json_header_added_when_dict_without_headers(self):
        response = Response({"message": "xxx"}, status_code=666)
        assert response.to_dict() == {
            "body": '{"message":"xxx"}',
            "headers": {"Content-Type": "application/json"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_response_body_passes_through_when_string(self):
        response = Response("xxx", headers={"xx": "xx"}, status_code=666)
        assert response.to_dict() == {
            "body": "xxx",
            "headers": {"xx": "xx"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_text_plain_header_added_when_string_without_headers(self):
        response = Response("xxx", status_code=666)
        assert response.to_dict() == {
            "body": "xxx",
            "headers": {"Content-Type": "text/plain"},
            "statusCode": 666,
            "isBase64Encoded": False,
        }

    def test_response_body_passes_through_when_base64(self):
        data = b64encode(b"xxx").decode("utf-8")
        response = Response(data, headers={"xx": "xx"}, status_code=666, base64_encoded=True)
        assert response.to_dict() == {
            "body": data,
            "headers": {"xx": "xx"},
            "statusCode": 666,
            "isBase64Encoded": True,
        }
