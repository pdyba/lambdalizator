# coding=utf-8

import pytest

from lbz.authz.utils import check_permission, has_permission
from lbz.dev.misc import Event
from lbz.exceptions import PermissionDenied, Unauthorized


class TestAuthorizationUtils:
    def test_check_permission(
        self, limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert check_permission(res_instance, "perm-name") == {"allow": "*", "deny": None}

    def test_check_permission_raises(
        self, limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/", "GET", headers={"authorization": limited_access_auth_header})
        )
        with pytest.raises(PermissionDenied):
            check_permission(res_instance, "garbage")

    def test_check_permission_unauthorised(
        self, sample_event, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(sample_event)
        with pytest.raises(Unauthorized):
            check_permission(res_instance, "perm-name")

    def test_has_permission_true(
        self, limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/garbage", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert has_permission(res_instance, "perm-name")

    def test_has_permission_false(
        self, limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            Event("/garbage", "GET", headers={"authorization": limited_access_auth_header})
        )
        assert not has_permission(res_instance, "garbage")
