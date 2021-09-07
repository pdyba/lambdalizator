# coding=utf-8
from http import HTTPStatus
from os import environ
from unittest.mock import patch

import pytest

from lbz.authz.decorators import authorization, check_permission, has_permission
from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route
from tests.fixtures.cognito_auth import env_mock


@patch.dict(environ, env_mock)
class TestAuthorizationDecorator:
    @pytest.fixture(autouse=True)
    def setup_class(self, auth_header, sample_event) -> None:
        class XResource(Resource):
            _name = "test_res"

            @add_route("/")
            @authorization("perm-name")
            def handler(self, restrictions) -> None:
                assert restrictions == {"allow": "*", "deny": None}
                return Response("x")

        self.res = XResource  # pylint: disable=attribute-defined-outside-init
        event = {**sample_event, "headers": {"authorization": auth_header}}
        self.res_instance = self.res(event)  # pylint: disable=attribute-defined-outside-init
        self.res_no_auth = self.res(sample_event)  # pylint: disable=attribute-defined-outside-init

    def teardown_method(self) -> None:
        self.res._authz_collector.clean()  # pylint: disable=protected-access

    def test_success(self, *_args) -> None:
        assert self.res_instance().status_code == HTTPStatus.OK

    def test_check_permission(self) -> None:
        assert check_permission(self.res_instance, "perm-name") == {"allow": "*", "deny": None}
        with pytest.raises(PermissionDenied):
            check_permission(self.res_instance, "garbage")
        with pytest.raises(Unauthorized):
            check_permission(self.res_no_auth, "perm-name")

    def test_has_permission(self) -> None:
        assert has_permission(self.res_instance, "perm-name")
        assert not has_permission(self.res_instance, "garbage")
