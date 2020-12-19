#!/usr/local/bin/python3.8
# coding=utf-8
from http import HTTPStatus
from os import environ
from unittest.mock import patch

from lbz.authz import Authorizer, authorization
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route
from tests import sample_private_key
from tests.fixtures.cognito_auth import env_mock
from tests.test_resource import event


class TestAuthorizationDecorator:
    @patch.dict(environ, env_mock)
    def test_success(self, *args):
        class X(Resource):
            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

        auth_header = Authorizer.sign_authz({"allow": "*", "deny": {}}, sample_private_key)
        resp = X({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

    @patch.dict(environ, env_mock)
    def test_no_auth_header(self, *args):
        class X(Resource):
            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                return Response("x")

        resp = X({**event, "headers": {}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.dict(environ, env_mock)
    def test_different_permission_name(self, *args):
        class X(Resource):
            @add_route("/")
            @authorization("perm-name")
            def handler(self, restrictions):
                assert restrictions == {"allow": "self", "deny": None}
                return Response("x")

        auth_header = Authorizer.sign_authz(
            {"allow": {"x": {"perm-name": {"allow": "self"}}}, "deny": {}}, sample_private_key
        )
        resp = X({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

        auth_header = Authorizer.sign_authz(
            {"allow": {"x": {"handler": {"allow": "*"}}}, "deny": {}}, sample_private_key
        )
        resp = X({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.FORBIDDEN

    @patch.dict(environ, env_mock)
    def test_different_class_name_success(self, *args):
        class X(Resource):
            _name = "test_res"

            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

        auth_header = Authorizer.sign_authz(
            {"allow": {"test_res": {"handler": {"allow": "*"}}}, "deny": {}}, sample_private_key
        )
        resp = X({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

        auth_header = Authorizer.sign_authz({"allow": {"x": "*"}, "deny": {}}, sample_private_key)
        resp = X({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.FORBIDDEN
