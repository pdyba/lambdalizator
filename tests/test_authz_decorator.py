# coding=utf-8
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from lbz.authz.decorators import authorization
from lbz.dev.misc import APIGatewayEvent
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route


class TestAuthorizationDecorator:
    @patch("lbz.authz.decorators.authz_collector")
    def test_authz_collectore_called(self, mocked_authz_collector: MagicMock) -> None:
        class XResource(Resource):  # pylint: disable=unused-variable
            _name = "test_res"

            @authorization("perm-name")
            def handler(self, restrictions: dict) -> None:
                pass

        mocked_authz_collector.add_authz.assert_called_once()

    def test_root_permissions_success(
        self, sample_resource_with_authorization, full_access_auth_header
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent("/", "GET", headers={"authorization": full_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.OK

    def test_limited_permissions_success(
        self, limited_access_auth_header, sample_resource_with_authorization
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent("/", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.OK

    def test_limited_permissions_failed(
        self, limited_access_auth_header, sample_resource_with_authorization
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent(
                "/garbage", "GET", headers={"authorization": limited_access_auth_header}
            )
        )
        assert res_instance().status_code == HTTPStatus.FORBIDDEN


class GuestResource(Resource):  # pylint: disable=unused-variable
    _name = "guest_res"

    @staticmethod
    def get_guest_authorization() -> dict:
        return {"allow": {"guest_res": {"handler": {"allow": "*"}}}, "deny": {}}

    @add_route("/")
    @authorization()
    def handler(self, restrictions: dict) -> Response:  # pylint: disable=unused-argument
        return Response("ok")

    @add_route("/garbage2")
    @authorization()
    def garbage(self, restrictions: dict) -> Response:  # pylint: disable=unused-argument
        return Response("ok")


class TestAuthorizationDecoratorGuestPermissions:
    def test_get_success(self) -> None:
        res_instance = GuestResource(APIGatewayEvent("/", "GET"))
        assert res_instance().status_code == HTTPStatus.OK

    def test_limited_permissions_failed(self) -> None:
        res_instance = GuestResource(APIGatewayEvent("/garbage2", "GET"))
        assert res_instance().status_code == HTTPStatus.FORBIDDEN

    def test_inharitance_success(
        self,
        full_access_auth_header,
    ) -> None:
        res_instance = GuestResource(
            APIGatewayEvent("/garbage2", "GET", headers={"authorization": full_access_auth_header})
        )
        assert res_instance().status_code == HTTPStatus.OK
