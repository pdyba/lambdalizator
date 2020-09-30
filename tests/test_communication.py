#!/usr/local/bin/python3.8
# coding=utf-8
import pytest

from lbz.response import Response
from lbz.request import Request
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict


class TestRequestInit:
    def test__init__(self):
        req = Request(
            headers={},
            uri_params={},
            method="",
            body="",
            context={},
            stage_vars={},
            is_base64_encoded=False,
            query_params=None,
            user=None,
        )
        assert isinstance(req.query_params, MultiDict)
        assert isinstance(req.headers, dict)
        assert isinstance(req.uri_params, dict)
        assert isinstance(req.uri_params, dict)
        assert isinstance(req.context, dict)
        assert isinstance(req.stage_vars, dict)
        assert isinstance(req.method, str)
        assert isinstance(req._body, str)
        assert isinstance(req._is_base64_encoded, bool)


class TestRequest:
    def setup_method(self, test_method):
        self.r = Request(
            headers={"Content-Type": "application/json"},
            uri_params={},
            method="GET",
            body="",
            context={},
            stage_vars={},
            is_base64_encoded=False,
            query_params=None,
            user=None,
        )

    def teardown_method(self, test_method):
        self.r = None

    def test___repr__(self):
        assert str(self.r) == f"<Request {self.r.method} >"

    def test__decode_base64_bytes(self):
        encoded = b"asdasdsd"
        output = Request._decode_base64(encoded)
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test__decode_base64_str(self):
        encoded = "asdasdsd"
        output = Request._decode_base64(encoded)
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_base64(self):
        self.r._body = b"asdasdsd"
        self.r._is_base64_encoded = True
        assert self.r.raw_body == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_bytes(self):
        self.r._body = b"asdasdsd"
        assert self.r.raw_body == b"asdasdsd"

    def test_raw_body_str(self):
        self.r._body = "abcx"
        assert self.r.raw_body == b"abcx"

    def test_json_body_dict(self):
        self.r._body = {"x": "abcx"}
        assert self.r.json_body == {"x": "abcx"}

    def test_json_body_json(self):
        self.r._json_body = None
        self.r._body = '{"x": "abcx"}'
        assert self.r.json_body == {"x": "abcx"}
        assert self.r._json_body == {"x": "abcx"}

    def test_json_body_bad_json(self):
        self.r._json_body = None
        self.r._body = '{"x": abcx}'
        with pytest.raises(BadRequestError):
            self.r.json_body

    def test_json_body_bad_content_type(self):
        self.r.headers = {"Content-Type": "application/dzejson"}
        with pytest.raises(BadRequestError) as err:
            self.r.json_body
            assert err.message.startswith("Content-Type header is missing or wrong")

    def test_json_body_none_when_no_content_type(self):
        self.r.headers = {}
        assert self.r.json_body is None

    def test_to_dict(self):
        assert self.r.to_dict() == {
            "context": {},
            "headers": {"Content-Type": "application/json"},
            "method": "GET",
            "query_params": {},
            "stage_vars": {},
            "uri_params": {},
            "user": None,
        }


class TestResponseInit:
    def test___init__(self):
        resp = Response({})
        assert isinstance(resp.body, dict)
        assert resp.headers == {"Content-Type": "application/json"}
        assert resp.status_code == 200
        assert not resp.base64

    def test___init__2(self):
        self.resp = Response("xxx", headers={"xx": "xx"}, status_code=666)
        assert isinstance(self.resp.body, dict)
        assert self.resp.body == {"message": "xxx"}
        assert self.resp.headers == {"xx": "xx"}
        assert self.resp.status_code == 666
        assert not self.resp.base64


class TestResponse:
    def setup_method(self):
        self.r = Response("xxx", headers={"xx": "xx"}, status_code=666)

    def teardown_method(self, test_method):
        self.r = None

    def test_to_dict(self):
        assert self.r.to_dict() == {
            "body": '{"message":"xxx"}',
            "headers": {"xx": "xx"},
            "statusCode": 666,
        }

    def test__encode_base64(self):
        with pytest.raises(ValueError):
            assert Response._encode_base64("xx")
        assert Response._encode_base64(b"xx") == "eHg="
