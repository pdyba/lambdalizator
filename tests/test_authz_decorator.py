# coding=utf-8
from http import HTTPStatus
from os import environ
from unittest.mock import patch

import pytest

from lbz.authz.authorizer import Authorizer
from lbz.authz.decorators import authorization, check_permission
from lbz.exceptions import PermissionDenied, Unauthorized
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

    def test_check_permission(self) -> None:
        # TODO: split into 3 test cases with improved testing (PR 40)
        class XResource(Resource):
            _name = "test_res"

            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

            def diff_perm(self):
                pass

        auth_header = Authorizer.sign_authz(
            {"allow": {"test_res": {"handler": {"allow": "*"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        res = XResource({**event, "headers": {"authorization": auth_header}})

        assert check_permission(res, "handler") == {"allow": "*", "deny": None}
        with pytest.raises(PermissionDenied):
            check_permission(res, "garbage")

        res = XResource({**event})
        with pytest.raises(Unauthorized):
            check_permission(res, "diff_perm")

    def test_check_permission_guest_policy(self) -> None:
        class XResource(Resource):
            _name = "test_res"

            @add_route("/")
            @authorization()
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

            def get_guest_authorization(self) -> dict:
                return {"allow": {"*": "*"}, "deny": {}}

        res = XResource({**event})
        assert check_permission(res, "handler") == {"allow": "*", "deny": None}
