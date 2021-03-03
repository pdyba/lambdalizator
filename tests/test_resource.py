#!/usr/local/bin/python3.8
# coding=utf-8
import json
from http import HTTPStatus
from os import environ
from unittest.mock import patch, MagicMock

from jose import jwt
from multidict import CIMultiDict

from lbz.authentication import User
from lbz.dev.misc import Event
from lbz.exceptions import NotFound, ServerError
from lbz.request import Request
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import Router
from lbz.router import add_route
from tests.fixtures.cognito_auth import env_mock

req = Request(
    headers=CIMultiDict({"Content-Type": "application/json"}),
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


class TestResource:
    def setup_method(self):
        self.res = Resource(event)

    def test___init__(self):
        assert isinstance(self.res.path, str)
        assert self.res.path == "/"
        assert isinstance(self.res.method, str)
        assert self.res.method == "GET"
        assert self.res.path_params == {}
        assert isinstance(self.res.request, Request)
        assert self.res._router is not None
        assert isinstance(self.res._router, Router)
        assert self.res.request.user is None

    @patch.object(Resource, "_get_user")
    def test___call__(self, get_user: MagicMock):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response({"message": "x"})

        cls = X(event)
        resp = cls()
        assert isinstance(resp, Response), resp
        assert resp.to_dict() == {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 200,
            "body": '{"message":"x"}',
            "isBase64Encoded": False,
        }
        get_user.assert_called_once_with({})

    def test_not_found_returned_when_path_not_defined(self):
        response = Resource(event_wrong_uri)()
        assert isinstance(response, Response)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_request_id_added_when_frameworks_exception_raised(self):
        class TestAPI(Resource):
            @add_route("/")
            def test_method(self):
                raise NotFound

        response = TestAPI(event)()

        assert response.body == {
            "message": NotFound.message,
            "request_id": event["requestContext"]["requestId"],
        }

    def test___repr__(self):
        self.res.urn = "/foo/id-12345/bar"
        assert str(self.res) == "<Resource GET @ /foo/id-12345/bar >"

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
        self, load_user: MagicMock, *args
    ):
        class X(Resource):
            @add_route("/")
            def a(self):
                return Response("x")

        key = json.loads(env_mock["ALLOWED_PUBLIC_KEYS"])["keys"][0]
        key_id = key["kid"]
        authentication_token = jwt.encode({"username": "x"}, "", headers={"kid": key_id})

        X({**event, "headers": {"authentication": authentication_token}})()
        load_user.assert_called_once_with(authentication_token)

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

    def test_pre_request_hook(self, *args):
        pre_request_called = False

        class TestAPI(Resource):
            @add_route("/")
            def test_method(self):
                return Response("OK")

            def pre_request_hook(self):
                nonlocal pre_request_called
                pre_request_called = True

        response = TestAPI(event)()

        assert response.body == "OK"
        assert pre_request_called

    def test_post_request_hook(self, *args):
        post_request_called = False

        class TestAPI(Resource):
            @add_route("/")
            def test_method(self):
                raise ServerError("test")

            def post_request_hook(self):
                nonlocal post_request_called
                post_request_called = True

        response = TestAPI(event)()

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert post_request_called
