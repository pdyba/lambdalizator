# coding=utf-8
from http import HTTPStatus
from os import environ
from unittest.mock import patch

from lbz.authz import Authorizer, authorization
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route
from tests import SAMPLE_PRIVATE_KEY
from tests.fixtures.cognito_auth import env_mock
from tests.test_resource import event


class TestAuthorizationDecorator:
    @patch.dict(environ, env_mock)
    def test_success(self, *_args):
        class XResource(Resource):
            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

        auth_header = Authorizer.sign_authz({"allow": "*", "deny": {}}, SAMPLE_PRIVATE_KEY)
        resp = XResource({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

    @patch.dict(environ, env_mock)
    def test_no_auth_header(self, *_args):
        class XResource(Resource):
            @add_route("/")
            @authorization()
            def handler(self, restrictions):  # pylint: disable=unused-argument
                return Response("x")

        resp = XResource({**event, "headers": {}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    @patch.dict(environ, env_mock)
    def test_no_auth_header_guest_in_place(self, *_args):
        class XResource(Resource):
            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

            @staticmethod
            def get_guest_authorization() -> dict:
                return {
                    "allow": "*",
                    "deny": {},
                }

        resp = XResource({**event, "headers": {}})()
        assert resp.status_code == 200

    @patch.dict(environ, env_mock)
    def test_different_permission_name(self, *_args):
        class XResource(Resource):
            @add_route("/")
            @authorization("perm-name")
            def handler(self, restrictions):
                assert restrictions == {"allow": "self", "deny": None}
                return Response("x")

        auth_header = Authorizer.sign_authz(
            {"allow": {"xresource": {"perm-name": {"allow": "self"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        resp = XResource({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

        auth_header = Authorizer.sign_authz(
            {"allow": {"xresource": {"handler": {"allow": "*"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        resp = XResource({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.FORBIDDEN

    @patch.dict(environ, env_mock)
    def test_different_class_name_success(self, *_args):
        class XResource(Resource):
            _name = "test_res"

            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

        auth_header = Authorizer.sign_authz(
            {"allow": {"test_res": {"handler": {"allow": "*"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        resp = XResource({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

        auth_header = Authorizer.sign_authz({"allow": {"x": "*"}, "deny": {}}, SAMPLE_PRIVATE_KEY)
        resp = XResource({**event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.FORBIDDEN
