# coding=utf-8
from copy import deepcopy
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call

import pytest

from lbz.authz.authorizer import Authorizer, ALL, ALLOW, DENY, LIMITED_ALLOW
from lbz.exceptions import PermissionDenied, SecurityRiskWarning, Unauthorized
from tests import SAMPLE_PRIVATE_KEY, EXPECTED_TOKEN


# pylint: disable=too-many-public-methods
class TestAuthorizerSetupClass:
    @staticmethod
    def _make_authorizer(token_payload: dict=None, jwt=None) -> Authorizer:
        if token_payload:
            jwt = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        return Authorizer(jwt, "test_resource", "permission_name")

    def test__init__(self, full_access_auth_header) -> None:
        authz = self._make_authorizer(jwt=full_access_auth_header)
        assert authz.allow == {ALL: ALL}
        assert authz.deny == {}
        assert authz.outcome == DENY
        assert authz.allowed_resource is None
        assert authz.allowed_resource is None
        assert authz.resource == "test_resource"
        assert authz.permission == "permission_name"

    def test__repr__(self, full_access_auth_header) -> None:
        authz = self._make_authorizer(jwt=full_access_auth_header)
        assert repr(authz) == (
            "Authorizer(auth_jwt=<jwt>, "
            "resource_name='test_resource', "
            "permission_name='permission_name')"
        )

    def test_validate_one_with_expired(self, full_access_authz_payload) -> None:
        expiration_negative = int((datetime.utcnow() - timedelta(seconds=1)).timestamp())
        with pytest.raises(Unauthorized):
            self._make_authorizer(token_payload={
                    **full_access_authz_payload,
                    "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
                    "exp": expiration_negative,
                }
            )


# pylint: disable=too-many-public-methods
class TestAuthorizerSetupMethod:
    @staticmethod
    def _make_mocked_authorizer(token_payload: dict) -> Authorizer:
        with patch("lbz.authz.authorizer.decode_jwt", lambda _: token_payload):
            return Authorizer("xx", "test_resource", "permission_name")


    def test_wrong_jwt_authz_payload_raises_permission_denied(self) -> None:
        with pytest.raises(PermissionDenied):
            self._make_mocked_authorizer({})

    def test_check_deny_res(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.deny = {"test_resource": ALL}
        with pytest.raises(PermissionDenied):
            authz._check_deny()  # pylint: disable=protected-access
        assert authz.outcome == DENY

    def test_check_allow_all(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW

    def test_check_deny_any(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.deny = {ALL: ALL}
        with pytest.raises(PermissionDenied):
            authz._check_deny()  # pylint: disable=protected-access
        assert authz.outcome == DENY

    def test_check_access_check_deny_outcome(self) -> None:
        authz = self._make_mocked_authorizer({"allow": {}, "deny": {ALL: ALL}})
        with pytest.raises(PermissionDenied):
            authz.check_access()

    def test_check_access_outcome_deny(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer({**full_access_authz_payload, "allow": {ALL: None}})
        with pytest.raises(PermissionDenied):
            authz.check_access()

    def test__check_resource(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        with patch.object(authz, "_deny_if_all", new_callable=MagicMock()) as mocked_deny:
            authz._check_resource({"res": "xxx"})  # pylint: disable=protected-access
            mocked_deny.assert_has_calls(
                [
                    call({"res": "xxx"}),
                    call("res"),
                    call("xxx"),
                ]
            )

    def test_validate_allow_all(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.check_access()
        assert authz.outcome == ALLOW
        assert authz.restrictions == {"allow": "*", "deny": None}

    def test_check_allow_fail_all(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allow = None
        with pytest.raises(PermissionDenied):
            authz._check_allow_and_set_resources()  # pylint: disable=protected-access
            assert authz.outcome == ALLOW

    def test_check_allow_domain(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allow = {"test_resource": ALL}
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW

    def test_check_allow_one(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allow = {"test_resource": {"permission_name": {"allow": ALL}}}
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW

    def test_check_allow_one_scope(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allow = {"test_resource": {"permission_name": {"allow": "self"}}}
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW
        assert authz.allowed_resource == "self"

    def test_check_allow_fail_one_scope(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allow = {"test_resource": {"permission_name": {"deny": "self"}}}
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW
        assert authz.denied_resource == "self"

    def test_get_restrictions_restricted(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allowed_resource = ALL
        authz.denied_resource = {"city": "warszawa"}
        assert authz.restrictions == {"allow": ALL, "deny": {"city": "warszawa"}}

    def test_check_deny_one_scope(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.deny = {"test_resource": {"permission_name": "self"}}
        authz._check_deny()  # pylint: disable=protected-access
        assert authz.denied_resource == "self"

    def test__set_policy_w_scope(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz._set_policy(  # pylint: disable=protected-access
            "",
            {
                **full_access_authz_payload,
                "allow": "Lambda",
                "deny": "Lambda",
            },
        )
        assert authz.allow == "Lambda"
        assert authz.deny == "Lambda"

    def test_deny_if_all(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        with pytest.raises(PermissionDenied):
            authz._deny_if_all(ALL)  # pylint: disable=protected-access

    def test_allow_if_all(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        assert authz._allow_if_allow_all(ALL)  # pylint: disable=protected-access
        assert authz.outcome == ALLOW
        assert authz.allowed_resource == ALL

    def test_check_deny_one(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.deny = {"test_resource": {"permission_name": ALL}}
        with pytest.raises(PermissionDenied):
            authz._check_deny()  # pylint: disable=protected-access
        assert authz.outcome == DENY

    def test_validate_fail_all(self, full_access_authz_payload) -> None:
        authorizer = self._make_mocked_authorizer({**full_access_authz_payload, "allow": {}})
        with pytest.raises(PermissionDenied):
            authorizer.check_access()
        assert authorizer.outcome == DENY

    def test_wrong_iss(self, full_access_authz_payload) -> None:
        with pytest.raises(PermissionDenied):
            self._make_mocked_authorizer({**full_access_authz_payload, "iss": "test2"})

    def test_validate_one(self, full_access_authz_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **full_access_authz_payload,
                "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "*", "deny": None}

    def test_validate_one_deprecation(self) -> None:
        with pytest.warns(DeprecationWarning):
            self._make_mocked_authorizer({"allow": "*", "deny": {}})
        with pytest.warns(SecurityRiskWarning):
            authorizer = self._make_mocked_authorizer({"allow": "*", "deny": {}})
        authorizer.check_access()
        assert authorizer.outcome == ALLOW

    def test_validate_one_scope(self, full_access_authz_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **full_access_authz_payload,
                "allow": {"test_resource": {"permission_name": {"allow": "self"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "self", "deny": None}

    def test_validate_fail_one_scope(self, full_access_authz_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **full_access_authz_payload,
                "allow": {"test_resource": {"permission_name": {"deny": "self"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == {"allow": None, "deny": "self"}

    def test_refs(self, full_access_authz_payload) -> None:
        restrictions = {"allow": "*", "deny": "example"}
        authorizer = self._make_mocked_authorizer(
            {
                **full_access_authz_payload,
                "refs": {"api-access": restrictions},
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == restrictions

    def test_missing_ref(self,full_access_authz_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **full_access_authz_payload,
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
            }
        )
        with pytest.raises(PermissionDenied):
            authorizer.check_access()
        assert authorizer.outcome == DENY

    def test_sign_authz(self) -> None:
        token = Authorizer.sign_authz({"allow": {ALL: ALL}, "deny": {}}, SAMPLE_PRIVATE_KEY)
        assert token == EXPECTED_TOKEN

    def test_sign_authz_not_a_dict_error(self) -> None:
        with pytest.raises(ValueError):
            Authorizer.sign_authz({"allow": {ALL: ALL}, "deny": {}}, "")

    def test_sign_authz_no_kid_error(self) -> None:
        prive_key = deepcopy(SAMPLE_PRIVATE_KEY)
        del prive_key["kid"]
        with pytest.raises(ValueError):
            Authorizer.sign_authz({"allow": {ALL: ALL}, "deny": {}}, prive_key)
