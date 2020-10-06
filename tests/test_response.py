#!/usr/local/bin/python3.8
# coding=utf-8
import pytest

from lbz.response import Response


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
