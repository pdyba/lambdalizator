# coding=utf-8

import pytest
from multidict import CIMultiDict

from lbz.exceptions import BadRequestError
from lbz.misc import MultiDict
from lbz.request import Request


class TestRequestInit:
    def test__init__(self):
        req = Request(
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


class TestRequest:
    @pytest.fixture(autouse=True)
    def setup_method(self, user):
        # pylint: disable=attribute-defined-outside-init
        self.request = Request(
            method="GET",
            uri_params={},
            body="",
            context={},
            headers=CIMultiDict({"Content-Type": "application/json"}),  # pylint issue #214
            stage_vars={},
            is_base64_encoded=False,
            query_params=None,
            user=user,
        )

    def teardown_method(self):
        # pylint: disable= attribute-defined-outside-init
        self.request = None

    def test___repr__(self):
        assert str(self.request) == f"<Request {self.request.method} >"

    def test__decode_base64_bytes(self):
        encoded = b"asdasdsd"
        output = Request._decode_base64(encoded)  # pylint: disable=protected-access
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test__decode_base64_str(self):
        encoded = "asdasdsd"
        output = Request._decode_base64(encoded)  # pylint: disable=protected-access
        assert output == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_base64(self):
        self.request._body = b"asdasdsd"  # pylint: disable=protected-access
        self.request._is_base64_encoded = True  # pylint: disable=protected-access
        assert self.request.raw_body == b"j\xc7Z\xb1\xdb\x1d"

    def test_raw_body_bytes(self):
        self.request._body = b"asdasdsd"  # pylint: disable=protected-access
        assert self.request.raw_body == b"asdasdsd"

    def test_raw_body_str(self):
        self.request._body = "abcx"  # pylint: disable=protected-access
        assert self.request.raw_body == b"abcx"

    def test_json_body_dict(self):
        self.request._body = '{"x": "abcx"}'  # pylint: disable=protected-access
        assert self.request.json_body == {"x": "abcx"}

    def test_json_body_json(self):
        self.request._json_body = None  # pylint: disable=protected-access
        self.request._body = '{"x": "abcx"}'  # pylint: disable=protected-access
        assert self.request.json_body == {"x": "abcx"}
        assert self.request._json_body == {"x": "abcx"}  # pylint: disable=protected-access

    def test_json_body_bad_json(self):
        self.request._json_body = None  # pylint: disable=protected-access
        self.request._body = '{"x": abcx}'  # pylint: disable=protected-access
        with pytest.raises(BadRequestError):
            self.request.json_body  # pylint: disable=pointless-statement

    def test_json_body_bad_content_type(self):
        self.request.headers = {"Content-Type": "application/dzejson"}
        with pytest.raises(BadRequestError) as err:
            self.request.json_body  # pylint: disable=pointless-statement
            assert err.message.startswith("Content-Type header is missing or wrong")

    def test_json_body_none_when_no_content_type(self):
        self.request.headers = {}
        assert self.request.json_body is None

    def test_accessing_user_attributes(self):
        assert isinstance(self.request.user.username, str)
        assert isinstance(self.request.user.email, str)
        for letter in ("1", "2", "3", "4", "5"):
            assert isinstance(getattr(self.request.user, letter), str)

    def test_headers_are_case_insensitive(self):
        assert self.request.headers["content-type"] == "application/json"
        assert self.request.headers["CoNtEnT-TyPe"] == "application/json"

    def test_to_dict(self):
        assert self.request.to_dict() == {
            "context": {},
            "headers": {"Content-Type": "application/json"},
            "method": "GET",
            "query_params": {},
            "stage_vars": {},
            "uri_params": {},
            "user": f"User username={self.request.user.username}",
        }
