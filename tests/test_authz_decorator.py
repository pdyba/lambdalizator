# coding=utf-8
from http import HTTPStatus
from unittest.mock import patch, MagicMock


from lbz.authz.decorators import authorization
from lbz.dev.misc import Event
from lbz.resource import Resource
from lbz.router import add_route
from lbz.response import Response


class TestAuthorizationDecorator:
    @patch("lbz.authz.decorators.authz_collector")
    def test_authz_collectore_called(self, mocked_authz_collector: MagicMock) -> None:
        class XResource(Resource):  # pylint: disable=unused-variable
            _name = "test_res"

            @authorization("perm-name")
            def handler(self, restrictions) -> None:
                pass

        mocked_authz_collector.add_authz.assert_called_once()

    def test_root_permissions_success(
        self, sample_resoruce_with_authorization, full_access_auth_header
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/", "GET", headers={"authorization": full_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.OK

    def test_limited_permissions_success(
        self, limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.OK

    def test_limited_permissions_failed(
        self, limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/garbage", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.FORBIDDEN


class GuestResource(Resource):  # pylint: disable=unused-variable
    _name = "guest_res"

    @staticmethod
    def get_guest_authorization() -> dict:
        return {"allow": {"guest_res": {"handler": {"allow": "*"}}}, "deny": {}}

    @add_route("/")
    @authorization()
    def handler(self, restrictions) -> Response:  # pylint: disable=unused-argument
        return Response("ok")

    @add_route("/garbage2")
    @authorization()
    def garbage(self, restrictions) -> Response:  # pylint: disable=unused-argument
        return Response("ok")


class TestAuthorizationDecoratorGuestPermissions:
    def test_get_success(self) -> None:
        res_instance = GuestResource(Event("/", "GET"))
        assert res_instance().status_code == HTTPStatus.OK

    def test_limited_permissions_failed(self) -> None:
        res_instance = GuestResource(Event("/garbage2", "GET"))
        assert res_instance().status_code == HTTPStatus.FORBIDDEN

    def test_inharitance_success(self, full_access_auth_header) -> None:
        res_instance = GuestResource(
            Event("/garbage2", "GET", headers={"authorization": full_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.OK
