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
    @pytest.fixture(autouse=True)
    def setup_class(self, base_auth_payload) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.token_payload = base_auth_payload
        self.authz = self._make_authorizer(self.token_payload)

    @staticmethod
    def _make_authorizer(token_payload: dict) -> Authorizer:
        jwt = Authorizer.sign_authz(token_payload, SAMPLE_PRIVATE_KEY)
        return Authorizer(jwt, "test_resource", "permission_name")

    def test__init__(self) -> None:
        assert self.authz.allow == {ALL: ALL}
        assert self.authz.deny == {}
        assert self.authz.outcome == DENY
        assert self.authz.allowed_resource is None
        assert self.authz.allowed_resource is None
        assert self.authz.resource == "test_resource"
        assert self.authz.permission == "permission_name"

    def test__repr__(self) -> None:
        assert repr(self.authz) == (
            "Authorizer(auth_jwt=<jwt>, "
            "resource_name='test_resource', "
            "permission_name='permission_name')"
        )

    def test_validate_one_with_expired(self) -> None:
        expiration_negative = int((datetime.utcnow() - timedelta(seconds=1)).timestamp())
        with pytest.raises(Unauthorized):
            self._make_authorizer(
                {
                    **self.token_payload,
                    "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
                    "exp": expiration_negative,
                }
            )


# pylint: disable=too-many-public-methods
class TestAuthorizerSetupMethod:
    @staticmethod
    def _mocked_make_authorizer(token_payload: dict) -> Authorizer:
        with patch("lbz.authz.authorizer.decode_jwt", lambda _: token_payload):
            return Authorizer("xx", "test_resource", "permission_name")

    @pytest.fixture(autouse=True)
    def setup_method(self, base_auth_payload) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.token_payload = base_auth_payload
        self.authz = self._mocked_make_authorizer(self.token_payload)

    def test_wrong_jwt_authz_payload_raises_permission_denied(self) -> None:
        with pytest.raises(PermissionDenied):
            self._mocked_make_authorizer({})

    def test_check_deny_res(self) -> None:
        self.authz.deny = {"test_resource": ALL}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.outcome == DENY

    def test_check_allow_all(self) -> None:
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW

    def test_check_deny_any(self) -> None:
        self.authz.deny = {ALL: ALL}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.outcome == DENY

    def test_check_access_check_deny(self) -> None:
        authz = self._mocked_make_authorizer({**self.token_payload, "deny": {ALL: ALL}})
        with pytest.raises(PermissionDenied):
            authz.check_access()

    def test_check_access_outcome_deny(self) -> None:
        authz = self._mocked_make_authorizer({**self.token_payload, "allow": {ALL: None}})
        with pytest.raises(PermissionDenied):
            authz.check_access()

    def test__check_resource(self) -> None:
        with patch.object(self.authz, "_deny_if_all", new_callable=MagicMock()) as mocked_deny:
            self.authz._check_resource({"res": "xxx"})  # pylint: disable=protected-access
            mocked_deny.assert_has_calls(
                [
                    call({"res": "xxx"}),
                    call("res"),
                    call("xxx"),
                ]
            )

    def test_validate_allow_all(self) -> None:
        self.authz.check_access()
        assert self.authz.outcome == ALLOW
        assert self.authz.restrictions == {"allow": "*", "deny": None}

    def test_check_allow_fail_all(self) -> None:
        self.authz.allow = None
        with pytest.raises(PermissionDenied):
            self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
            assert self.authz.outcome == ALLOW

    def test_check_allow_domain(self) -> None:
        self.authz.allow = {"test_resource": ALL}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW

    def test_check_allow_one(self) -> None:
        self.authz.allow = {"test_resource": {"permission_name": {"allow": ALL}}}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW

    def test_check_allow_one_scope(self) -> None:
        self.authz.allow = {"test_resource": {"permission_name": {"allow": "self"}}}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == "self"

    def test_check_allow_fail_one_scope(self) -> None:
        self.authz.allow = {"test_resource": {"permission_name": {"deny": "self"}}}
        self.authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW
        assert self.authz.denied_resource == "self"

    def test_get_restrictions_restricted(self) -> None:
        self.authz.allowed_resource = ALL
        self.authz.denied_resource = {"city": "warszawa"}
        assert self.authz.restrictions == {"allow": ALL, "deny": {"city": "warszawa"}}

    def test_check_deny_one_scope(self) -> None:
        self.authz.deny = {"test_resource": {"permission_name": "self"}}
        self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.denied_resource == "self"

    def test__set_policy_w_scope(self) -> None:
        self.authz._set_policy(  # pylint: disable=protected-access
            "",
            {
                **self.token_payload,
                "allow": "Lambda",
                "deny": "Lambda",
            },
        )
        assert self.authz.allow == "Lambda"
        assert self.authz.deny == "Lambda"

    def test_deny_if_all(self) -> None:
        with pytest.raises(PermissionDenied):
            self.authz._deny_if_all(ALL)  # pylint: disable=protected-access

    def test_allow_if_all(self) -> None:
        assert self.authz._allow_if_allow_all(ALL)  # pylint: disable=protected-access
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == ALL

    def test_check_deny_one(self) -> None:
        self.authz.deny = {"test_resource": {"permission_name": ALL}}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()  # pylint: disable=protected-access
        assert self.authz.outcome == DENY

    def test_validate_fail_all(self) -> None:
        authorizer = self._mocked_make_authorizer({**self.token_payload, "allow": {}})
        with pytest.raises(PermissionDenied):
            authorizer.check_access()
        assert authorizer.outcome == DENY

    def test_wrong_iss(self) -> None:
        with pytest.raises(PermissionDenied):
            self._mocked_make_authorizer({**self.token_payload, "iss": "test2"})

    def test_validate_one(self) -> None:
        authorizer = self._mocked_make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "*", "deny": None}

    def test_validate_one_deprecation(self) -> None:
        with pytest.warns(DeprecationWarning):
            self._mocked_make_authorizer({"allow": "*", "deny": {}})
        with pytest.warns(SecurityRiskWarning):
            authorizer = self._mocked_make_authorizer({"allow": "*", "deny": {}})
        authorizer.check_access()
        assert authorizer.outcome == ALLOW

    def test_validate_one_scope(self) -> None:
        authorizer = self._mocked_make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"allow": "self"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "self", "deny": None}

    def test_validate_fail_one_scope(self) -> None:
        authorizer = self._mocked_make_authorizer(
            {
                **self.token_payload,
                "allow": {"test_resource": {"permission_name": {"deny": "self"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == {"allow": None, "deny": "self"}

    def test_refs(self) -> None:
        restrictions = {"allow": "*", "deny": "example"}
        authorizer = self._mocked_make_authorizer(
            {
                **self.token_payload,
                "refs": {"api-access": restrictions},
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == restrictions

    def test_missing_ref(self) -> None:
        authorizer = self._mocked_make_authorizer(
            {
                **self.token_payload,
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
