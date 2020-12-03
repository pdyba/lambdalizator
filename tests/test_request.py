#!/usr/local/bin/python3.8
# coding=utf-8
from uuid import uuid4

import pytest

from lbz.authentication import User
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict
from lbz.request import Request
from tests.utils import encode_token


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
        assert req.user is None


class TestRequest:
    def setup_method(self):
        self.cognito_user = {
            "cognito:username": str(uuid4()),
            "email": f"{str(uuid4())}@{str(uuid4())}.com",
            "custom:a": str(uuid4()),
            "custom:b": str(uuid4()),
            "custom:c": str(uuid4()),
            "custom:d": str(uuid4()),
            "custom:e": str(uuid4()),
        }
        self.id_token = encode_token(self.cognito_user)
        self.r = Request(
            headers={"Content-Type": "application/json"},
            uri_params={},
            method="GET",
            body="",
            context={},
            stage_vars={},
            is_base64_encoded=False,
            query_params=None,
            user=User(self.id_token),
        )

    def teardown_method(self):
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

    def test_accessing_user_attributes(self):
        assert isinstance(self.r.user.username, str)
        assert isinstance(self.r.user.email, str)
        for letter in ("a", "b", "c", "d", "e"):
            assert isinstance(getattr(self.r.user, letter), str)

    def test_to_dict(self):
        assert self.r.to_dict() == {
            "context": {},
            "headers": {"Content-Type": "application/json"},
            "method": "GET",
            "query_params": {},
            "stage_vars": {},
            "uri_params": {},
            "user": f"User username={self.r.user.username}",
        }
