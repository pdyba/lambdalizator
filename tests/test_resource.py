#!/usr/local/bin/python3.8
# coding=utf-8
import pytest

from os import environ
from unittest.mock import patch

from lbz.authentication import User
from lbz.exceptions import Unauthorized
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
    def test_user_loaded_on_init(self, get_user_mock):
        self.res = Resource(event)
        get_user_mock.assert_called_once_with({})

    def test___call__wrong_uri(self):
        resp = self.res()
        assert isinstance(resp, Response)
        assert resp.to_dict() == {
            "body": '{"message":"Server is not able to produce a response"}',
            "headers": {},
            "statusCode": 421,
        }

    def test___call__(self):
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

    def test___repr__(self):
        assert str(self.res) == "<Resource GET @ / UIDS: {}>"

    def test_unauthorized_when_authentication_not_configured(self):
        with pytest.raises(Unauthorized):
            Resource({**event, "headers": {"authentication": "dummy"}})

    @patch.dict(environ, env_mock)
    @patch.object(User, "__init__", return_value=None)
    def test_user_loaded_when_cognito_authentication_configured(
        self, load_cognito_user_mock, *args
    ):
        Resource({**event, "headers": {"authentication": "dummy"}})
        load_cognito_user_mock.assert_called_once_with(
            "dummy",
            env_mock["COGNITO_PUBLIC_JWK"],
            env_mock["COGNITO_POOL_ID"],
        )

    def test_get_guest_authorization(self):
        atz = self.res.get_guest_authorization()
        assert (
            atz
            == "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.rv8AvMUIdiOqrK7CscYoxc53OgqP1L76k4xd9hBv-218EYbcU5n52Tg7rWzjsxQ_9ig18vJFjk5WeHkQsMZ_rQ"  # noqa: E501
        )
