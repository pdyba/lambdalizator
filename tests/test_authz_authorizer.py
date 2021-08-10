# coding=utf-8
from datetime import datetime, timedelta

import pytest

from lbz.authz import Authorizer, ALL, ALLOW, DENY, LIMITED_ALLOW
from lbz.exceptions import PermissionDenied, SecurityRiskWarning, Unauthorized
from tests import SAMPLE_PRIVATE_KEY, EXPECTED_TOKEN


# pylint: disable=too-many-public-methods
class TestAuthorizer:
    def setup_method(self):
        # pylint: disable=attribute-defined-outside-init
        self.iat = int(datetime.utcnow().timestamp())
        self.exp = int((datetime.utcnow() + timedelta(hours=6)).timestamp())
        self.iss = "test-issuer"
        self.token_payload = {
            "allow": {ALL: ALL},
            "deny": {},
            "exp": self.exp,
            "iat": self.iat,
            "iss": self.iss,
        }
        self.authz = self._make_authorizer(self.token_payload)

    @staticmethod
    def _make_authorizer(token_payload: dict) -> Authorizer:
        jwt = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        return Authorizer(jwt, "test_resource", "permission_name")

    def test__init__(self):
        assert self.authz.allow == {ALL: ALL}
        assert self.authz.deny == {}
        assert self.authz.outcome == DENY
        assert self.authz.allowed_resource is None
        assert self.authz.allowed_resource is None
        assert self.authz.resource == "test_resource"
        assert self.authz.permission == "permission_name"

    def test__repr__(self):
        expected_repr = "Authorizer(auth_jwt=<jwt>, resource_name='test_resource', permission_name='permission_name')"
        assert repr(self.authz) == expected_repr

    def test__set_policy_w_scope(self):
        self.authz._set_policy(  # pylint: disable=protected-access
            "", {"allow": "Lambda", "deny": "Lambda"}
        )
        assert self.authz.allow == "Lambda"
        assert self.authz.deny == "Lambda"

    def test_validate_allow_all(self):
        self.authz.check_access()
        assert self.authz.outcome == ALLOW
        assert self.authz.restrictions == {"allow": "*", "deny": None}

    def test_validate_fail_all(self):
        authorizer = self._make_authorizer({**self.token_payload, "allow": {}})
        with pytest.raises(PermissionDenied):
            authorizer.check_access()
        assert authorizer.outcome == DENY

    def test_wrong_iss(self):
        with pytest.raises(PermissionDenied):
            self._make_authorizer({**self.token_payload, "iss": "test2"})

    def test_validate_one(self):
        authorizer = self._make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "*", "deny": None}

    def test_validate_one_deprecation(self):
        with pytest.warns(DeprecationWarning):
            self._make_authorizer({"allow": "*", "deny": {}})
        with pytest.warns(SecurityRiskWarning):
            authorizer = self._make_authorizer({"allow": "*", "deny": {}})
        authorizer.check_access()
        assert authorizer.outcome == ALLOW

    def test_validate_one_with_expired(self):
        expiration_negative = int((datetime.utcnow() - timedelta(seconds=1)).timestamp())

        with pytest.raises(Unauthorized):
            self._make_authorizer(
                {
                    **self.token_payload,
                    "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
                    "exp": expiration_negative,
                }
            )

    def test_validate_one_scope(self):
        authorizer = self._make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"allow": "self"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "self", "deny": None}

    def test_validate_fail_one_scope(self):
        authorizer = self._make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"deny": "self"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == {"allow": None, "deny": "self"}

    def test_refs(self):
        restrictions = {"allow": "*", "deny": "example"}
        authorizer = self._make_authorizer(
            {
                **self.token_payload,
                "refs": {"api-access": restrictions},
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == restrictions

    def test_missing_ref(self):
        authorizer = self._make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
            }
        )
        with pytest.raises(PermissionDenied):
            authorizer.check_access()
        assert authorizer.outcome == DENY

    def test_deny_if_all(self):
        with pytest.raises(PermissionDenied):
            self.authz._deny_if_all(ALL)  # pylint: disable=protected-access

    def test_check_deny_any(self):
        self.authz.deny = {ALL: ALL}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.outcome == DENY

    def test_check_deny_res(self):
        self.authz.deny = {"test_resource": ALL}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.outcome == DENY

    def test_check_deny_one(self):
        self.authz.deny = {"test_resource": {"permission_name": ALL}}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.outcome == DENY

    def test_check_deny_one_scope(self):
        self.authz.deny = {"test_resource": {"permission_name": "self"}}
        self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.denied_resource == "self"

    def test_allow_if_all(self):
        assert self.authz._allow_if_allow_all(ALL)  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == ALL

    def test_check_allow_all(self):
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW

    def test_check_allow_fail_all(self):
        self.authz.allow = None
        with pytest.raises(PermissionDenied):
            self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
            assert self.authz.outcome == ALLOW

    def test_check_allow_one(self):
        self.authz.allow = {"test_resource": {"permission_name": {"allow": ALL}}}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW

    def test_check_allow_one_scope(self):
        self.authz.allow = {"test_resource": {"permission_name": {"allow": "self"}}}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == "self"

    def test_check_allow_fail_one_scope(self):
        self.authz.allow = {"test_resource": {"permission_name": {"deny": "self"}}}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW
        assert self.authz.denied_resource == "self"

    def test_get_restrictions_restricted(self):
        self.authz.allowed_resource = ALL
        self.authz.denied_resource = {"city": "warszawa"}
        assert self.authz.restrictions == {"allow": ALL, "deny": {"city": "warszawa"}}

    def test_sign_authz(self):
        token = Authorizer.sign_authz({"allow": {ALL: ALL}, "deny": {}}, SAMPLE_PRIVATE_KEY)
        assert token == EXPECTED_TOKEN
