# coding=utf-8
from http import HTTPStatus
from os import environ
from unittest.mock import patch

import pytest

from lbz.authz.authorizer import Authorizer
from lbz.authz.decorators import authorization, check_permission, has_permission
from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route
from tests import SAMPLE_PRIVATE_KEY
from tests.fixtures.cognito_auth import env_mock


@patch.dict(environ, env_mock)
class TestAuthorizationDecorator:
    @pytest.fixture(autouse=True)
    def setup_method(self, sample_event):
        class XResource(Resource):
            @add_route("/")
            @authorization("perm-name")
            def handler(self, restrictions):
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

        self.res = XResource  # pylint: disable=attribute-defined-outside-init
        self.event = sample_event  # pylint: disable=attribute-defined-outside-init

    def test_success(self, *_args):
        auth_header = Authorizer.sign_authz({"allow": "*", "deny": {}}, SAMPLE_PRIVATE_KEY)
        resp = self.res({**self.event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

    def test_no_auth_header(self, *_args):
        resp = self.res({**self.event, "headers": {}})()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_no_auth_header_guest_in_place(self, *_args):
        class XResource(self.res):
            @staticmethod
            def get_guest_authorization() -> dict:
                return {
                    "allow": "*",
                    "deny": {},
                }

        resp = XResource({**self.event, "headers": {}})()
        assert resp.status_code == 200

    def test_different_permission_name_ok(self, *_args):
        auth_header = Authorizer.sign_authz(
            {"allow": {"xresource": {"perm-name": {"allow": "*"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        resp = self.res({**self.event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

    def test_different_permission_name_forbidden(self, *_args):
        auth_header = Authorizer.sign_authz(
            {"allow": {"xresource": {"handler": {"allow": "*"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        resp = self.res({**self.event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.FORBIDDEN

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
        resp = XResource({**self.event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.OK

        auth_header = Authorizer.sign_authz({"allow": {"x": "*"}, "deny": {}}, SAMPLE_PRIVATE_KEY)
        resp = XResource({**self.event, "headers": {"authorization": auth_header}})()
        assert resp.status_code == HTTPStatus.FORBIDDEN


class TestCheckPermissionHasPermission:
    @pytest.fixture(autouse=True)
    def setup_method(self, sample_event):
        class XResource(Resource):
            _name = "test_res"

            @add_route("/")
            def handler(self):
                return Response("x")

        auth_header = Authorizer.sign_authz(
            {"allow": {"test_res": {"handler": {"allow": "*"}}}, "deny": {}},
            SAMPLE_PRIVATE_KEY,
        )
        event = {**sample_event, "headers": {"authorization": auth_header}}
        self.res = XResource(event)  # pylint: disable=attribute-defined-outside-init
        self.res_no_auth = XResource(  # pylint: disable=attribute-defined-outside-init
            {**sample_event}
        )

    def test_check_permission(self):
        assert check_permission(self.res, "handler") == {"allow": "*", "deny": None}
        with pytest.raises(PermissionDenied):
            check_permission(self.res, "garbage")
        with pytest.raises(Unauthorized):
            check_permission(self.res_no_auth, "handler")

    def test_has_permission(self):
        assert has_permission(self.res, "handler")
        assert not has_permission(self.res, "garbage")
