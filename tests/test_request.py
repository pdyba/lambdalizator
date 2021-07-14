#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access, too-few-public-methods
from uuid import uuid4

import pytest
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict
from lbz.request import Request
from tests.utils import encode_token


class TestRequestInit:
    def test__init__(self):
        req = Request(
            headers=CIMultiDict(),
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
        assert isinstance(req.headers, CIMultiDict)
        assert isinstance(req.uri_params, dict)
        assert isinstance(req.uri_params, dict)
        assert isinstance(req.context, dict)
        assert isinstance(req.stage_vars, dict)
        assert isinstance(req.method, str)
        assert isinstance(req._body, str)
        assert isinstance(req._is_base64_encoded, bool)
        assert req.user is None


class TestRequest: # pylint: disable=attribute-defined-outside-init
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
        self.resp = Request(
            headers=CIMultiDict({"Content-Type": "application/json"}),
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
        self.resp = None

    def test___repr__(self):
        assert str(self.resp) == f"<Request {self.resp.method} >"

    def test__decode_base64_bytes(self):
        encoded = b"asdasdsd"
        output = Request._decode_base64(encoded)
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test__decode_base64_str(self):
        encoded = "asdasdsd"
        output = Request._decode_base64(encoded)
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_base64(self):
        self.resp._body = b"asdasdsd"
        self.resp._is_base64_encoded = True
        assert self.resp.raw_body == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_bytes(self):
        self.resp._body = b"asdasdsd"
        assert self.resp.raw_body == b"asdasdsd"

    def test_raw_body_str(self):
        self.resp._body = "abcx"
        assert self.resp.raw_body == b"abcx"

    def test_json_body_dict(self):
        self.resp._body = {"x": "abcx"}
        assert self.resp.json_body == {"x": "abcx"}

    def test_json_body_json(self):
        self.resp._json_body = None
        self.resp._body = '{"x": "abcx"}'
        assert self.resp.json_body == {"x": "abcx"}
        assert self.resp._json_body == {"x": "abcx"}

    def test_json_body_bad_json(self):
        self.resp._json_body = None
        self.resp._body = '{"x": abcx}'
        with pytest.raises(BadRequestError):
            self.resp.json_body  # pylint: disable=pointless-statement

    def test_json_body_bad_content_type(self):
        self.resp.headers = {"Content-Type": "application/dzejson"}
        with pytest.raises(BadRequestError) as err:
            self.resp.json_body  # pylint: disable=pointless-statement
            assert err.message.startswith("Content-Type header is missing or wrong")

    def test_json_body_none_when_no_content_type(self):
        self.resp.headers = {}
        assert self.resp.json_body is None

    def test_accessing_user_attributes(self):
        assert isinstance(self.resp.user.username, str)
        assert isinstance(self.resp.user.email, str)
        for letter in ("a", "b", "c", "d", "e"):
            assert isinstance(getattr(self.resp.user, letter), str)

    def test_headers_are_case_insensitive(self):
        assert (
                self.resp.headers["content-type"] == self.resp.headers["CoNtEnT-TyPe"] == "application/json"
        )

    def test_to_dict(self):
        assert self.resp.to_dict() == {
            "context": {},
            "headers": {"Content-Type": "application/json"},
            "method": "GET",
            "query_params": {},
            "stage_vars": {},
            "uri_params": {},
            "user": f"User username={self.resp.user.username}",
        }
