# coding=utf-8

import pytest

from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.authz.utils import has_permission, check_permission


class TestAuthorizationDecorator:
    @pytest.mark.parametrize(
        "sample_event_with_limited_access_auth_header",
        [{"path": "/"}],
        indirect=True,
    )
    def test_check_permission(
        self, sample_event_with_limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            sample_event_with_limited_access_auth_header
        )
        assert check_permission(res_instance, "perm-name") == {"allow": "*", "deny": None}
        with pytest.raises(PermissionDenied):
            check_permission(res_instance, "garbage")

    def test_check_permission_unathorised(
        self, sample_event, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(sample_event)
        with pytest.raises(Unauthorized):
            check_permission(res_instance, "perm-name")

    @pytest.mark.parametrize(
        "sample_event_with_limited_access_auth_header",
        [{"path": "/garbage"}],
        indirect=True,
    )
    def test_has_permission(
        self, sample_event_with_limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            sample_event_with_limited_access_auth_header
        )
        assert has_permission(res_instance, "perm-name")
        assert not has_permission(res_instance, "garbage")
