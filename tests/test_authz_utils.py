# coding=utf-8
from typing import Type

import pytest

from lbz.authz.utils import check_permission, has_permission
from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.resource import Resource
from lbz.rest import APIGatewayEvent


class TestAuthorizationUtils:
    def test_check_permission(
        self, limited_access_auth_header: str, sample_resource_with_authorization: Type[Resource]
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent("/", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert check_permission(res_instance, "perm-name") == {"allow": "*", "deny": None}

    def test_check_permission_raises(
        self, limited_access_auth_header: str, sample_resource_with_authorization: Type[Resource]
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent("/", "GET", headers={"authorization": limited_access_auth_header})
        )
        with pytest.raises(PermissionDenied):
            check_permission(res_instance, "garbage")

    def test_check_permission_unauthorised(
        self, sample_event: APIGatewayEvent, sample_resource_with_authorization: Type[Resource]
    ) -> None:
        res_instance = sample_resource_with_authorization(sample_event)
        with pytest.raises(Unauthorized):
            check_permission(res_instance, "perm-name")

    def test_has_permission_true(
        self, limited_access_auth_header: str, sample_resource_with_authorization: Type[Resource]
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent(
                "/garbage", "GET", headers={"authorization": limited_access_auth_header}
            )
        )
        assert has_permission(res_instance, "perm-name")

    def test_has_permission_false(
        self, limited_access_auth_header: str, sample_resource_with_authorization: Type[Resource]
    ) -> None:
        res_instance = sample_resource_with_authorization(
            APIGatewayEvent(
                "/garbage", "GET", headers={"authorization": limited_access_auth_header}
            )
        )
        assert not has_permission(res_instance, "garbage")
