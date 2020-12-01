#!/usr/local/bin/python3.8
# coding=utf-8
import json

from http import HTTPStatus
from os import environ
from unittest.mock import patch

from jose import jwt

from lbz.authentication import User
from lbz.resource import Resource
from lbz.router import Router
from lbz.router import add_route
from lbz.request import Request
from lbz.response import Response
from lbz.dev.misc import Event
from lbz.authz import Authorizer
from tests.fixtures.cognito_auth import env_mock

req = Request(
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

event = Event(
    resource_path="/",
    method="GET",
    headers={},
    path_params={},
    query_params={},
    body=req,
)

event_wrong_uri = Event(
    resource_path="/xxxs/asdasd/xxx",
    method="GET",
    headers={},
    path_params={},
    query_params={},
    body=req,
)


class TestResourceWrongUri:
    def setup_method(self):
        self.res = Resource(event_wrong_uri)

    def test___call__wrong_uri(self):
        resp = self.res()
        assert isinstance(resp, Response)
        assert resp.to_dict() == {
            "body": '{"message":"Server is not able to produce a response"}',
            "headers": {},
            "statusCode": 421,
        }


class TestResource:
    def setup_method(self):
        self.res = Resource(event)

    def test___init__(self):
        assert isinstance(self.res.path, str)
        assert self.res.path == "/"
        assert isinstance(self.res.method, str)
        assert self.res.method == "GET"
        assert self.res.uids == {}
        assert isinstance(self.res.request, Request)
        assert self.res._authorizer is not None
        assert isinstance(self.res._authorizer, Authorizer)
        assert self.res._router is not None
        assert isinstance(self.res._router, Router)
        assert self.res.request.user is None

    @patch.object(Resource, "_get_user")
    def test___call__(self, get_user_mock):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        cls = X(event)
        resp = cls()
        assert isinstance(resp, Response), resp
        assert resp.to_dict() == {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 200,
            "body": '{"message":"x"}',
        }
        get_user_mock.assert_called_once_with({})

    def test___repr__(self):
        assert str(self.res) == "<Resource GET @ / UIDS: {}>"

    def test_unauthorized_when_authentication_not_configured(self):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        resp = X({**event, "headers": {"authentication": "dummy"}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.dict(environ, env_mock)
    @patch.object(User, "__init__", return_value=None)
    def test_user_loaded_when_cognito_authentication_configured_correctly(
        self, load_cognito_user_mock, *args
    ):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        key = json.loads(env_mock["ALLOWED_PUBLIC_KEYS"])["keys"][0]
        key_id = key["kid"]
        authentication_token = jwt.encode({"username": "x"}, "", headers={"kid": key_id})

        X({**event, "headers": {"authentication": authentication_token}})()
        load_cognito_user_mock.assert_called_once_with(authentication_token)

    @patch.dict(environ, env_mock)
    def test_unauthorized_when_jwt_header_lacks_kid(self, *args):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        authentication_token = jwt.encode({"foo": "bar"}, "")
        resp = X({**event, "headers": {"authentication": authentication_token}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.dict(environ, env_mock)
    def test_unauthorized_when_no_matching_key_in_env_variable(self, *args):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        authentication_token = jwt.encode({"kid": "foobar"}, "")
        resp = X({**event, "headers": {"authentication": authentication_token}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.dict(environ, env_mock)
    def test_unauthorized_when_jwt_header_malformed(self, *args):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        resp = X({**event, "headers": {"authentication": "12345"}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_guest_authorization_returns_root_by_default(self):
        atz = self.res.get_guest_authorization()
        assert (
            atz
            == "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk0OTRhZDc1LTNmNTQtNDE1NS04NGZhLWMxYTE3ZGEyMmIzNSIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.nDqCxO2Q1iXpxzbH7syxuyqw7kCY0sDfi9RX-VSUMTRN5aWTLt1bcPw4oN_jx89-YHBzDwnwBc07RsMgpFuo4zz2LU9PF0ciYxMNX-atTNsaIn05NkXT08au2AYb0DRCDS76MZ4QNi-4mRpLrj1SD4mSCwGtc2WNw9f0J0Vm4ZCYPVW6BqpcHcaFXzcFZ6EIoooaK6GvdTOjy498lWsAXjAen2U6Jles_BwFjqW1lW_ky4WV4J9NnK3v5wWKgR1Pg4R4LpnhIXe0dU_l64JHoJA3YcYxl-qilHfoBduc3La4kRKk7FAQDIqbOv4uN03BIoDXLH5t2uJ1Sm79Pe0ngGd5pSBmfUDKOGsHtx_3_9ZKfp-E2IVS0C7r36p4Ue0gKQzn0pXxa591bxm_puJAQ399SdbmlOJsM2cVFYAtlUQvWgErc57WcUJ0Qe4jEycury7hagNbP2fLn-7Gg4gZHiZ_Ul7L6GukbDfCHnhxSS4P3t3cVtWuslZi16hDhNbOTKD95y7PXvHePvI57ALV2v0RecQ5Blwurt1OuDRSjCYXyO6U4Y9MBHcd1wMtDoVW0jjvjXvqkEhuB52Zajh_yTNnJo0OAHpuK5wldVpECGFVx1rkW1ypKqlukGIgD--m6ElKnl6jw5VWSbdh2TJsZHnzjovbQUeqZOeMxwX6SE8"
            # noqa: E501
        )
