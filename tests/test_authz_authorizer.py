# coding=utf-8
import logging
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

import pytest
from pytest import LogCaptureFixture

from lbz.authz.authorizer import ALL, ALLOW, DENY, LIMITED_ALLOW, Authorizer
from lbz.exceptions import PermissionDenied, Unauthorized
from tests import EXPECTED_TOKEN, SAMPLE_PRIVATE_KEY


class TestAuthorizerWithoutMockingJWT:
    def test__init__(self, full_access_auth_header) -> None:
        authz = Authorizer(full_access_auth_header, "test_resource", "permission_name")
        assert authz.allow == {ALL: ALL}
        assert authz.deny == {}
        assert authz.outcome == DENY
        assert authz.allowed_resource is None
        assert authz.allowed_resource is None
        assert authz.resource == "test_resource"
        assert authz.permission == "permission_name"

    def test__repr__(self, full_access_auth_header) -> None:
        authz = Authorizer(full_access_auth_header, "test_resource", "permission_name")
        assert repr(authz) == (
            "Authorizer(auth_jwt=<jwt>, "
            "resource_name='test_resource', "
            "permission_name='permission_name')"
        )

    def test_validate_one_with_expired(self, full_access_authz_payload) -> None:
        expired_timestamp = int((datetime.utcnow() - timedelta(seconds=1)).timestamp())
        with pytest.raises(Unauthorized):
            Authorizer(
                Authorizer.sign_authz(
                    {
                        **full_access_authz_payload,
                        "exp": expired_timestamp,
                    },
                    SAMPLE_PRIVATE_KEY,
                ),
                "test_resource",
                "permission_name",
            )


# pylint: disable=too-many-public-methods
class TestAuthorizerWithMockedJWT:
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

    def test__check_access__outcome_deny_bcs_deny_all(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {},
                "deny": {ALL: ALL},  # this is to overwrite allow but keep iss/aud etc.
            }
        )
        with pytest.raises(PermissionDenied):
            authz.check_access()

    def test__check_access__outcome_deny_bcs_allow_none(self, full_access_authz_payload) -> None:
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

    def test_check_allow_fail_all(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer({**jwt_partial_payload, "allow": {}, "deny": {}})
        with pytest.raises(PermissionDenied):
            authz._check_allow_and_set_resources()  # pylint: disable=protected-access
            assert authz.outcome == ALLOW

    def test_check_allow_resource(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(
            {**jwt_partial_payload, "allow": {"test_resource": ALL}, "deny": {}}
        )
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW

    def test_check_allow_one(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
                "deny": {},
            }
        )
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW

    def test_check_allow_one_scope(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"allow": "self"}}},
                "deny": {},
            }
        )
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW
        assert authz.allowed_resource == "self"

    def test_check_allow_fail_one_scope(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"deny": "self"}}},
                "deny": {},
            }
        )
        authz._check_allow_and_set_resources()  # pylint: disable=protected-access
        assert authz.outcome == ALLOW
        assert authz.denied_resource == "self"

    def test_get_restrictions_restricted(self, full_access_authz_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        authz.allowed_resource = ALL
        authz.denied_resource = {"city": "warszawa"}
        assert authz.restrictions == {"allow": ALL, "deny": {"city": "warszawa"}}

    def test_check_deny_one_scope(self, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {},
                "deny": {"test_resource": {"permission_name": "self"}},
            }
        )
        authz._check_deny()  # pylint: disable=protected-access
        assert authz.denied_resource == "self"

    def test__set_policy_w_scope(self, full_access_authz_payload, jwt_partial_payload) -> None:
        authz = self._make_mocked_authorizer(full_access_authz_payload)
        permission_payload = {
            **jwt_partial_payload,
            "allow": "Lambda",
            "deny": "Lambda",
        }
        authz._set_policy(  # pylint: disable=protected-access
            base_permission_policy=permission_payload,
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

    def test_validate_one(self, jwt_partial_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"allow": ALL}}},
                "deny": {},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "*", "deny": None}

    def test_validate_one_scope(self, jwt_partial_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"allow": "self"}}},
                "deny": {},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "self", "deny": None}

    def test_validate_fail_one_scope(self, jwt_partial_payload) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"deny": "self"}}},
                "deny": {},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == {"allow": None, "deny": "self"}

    def test_refs(self, jwt_partial_payload) -> None:
        restrictions = {"allow": "*", "deny": "example"}
        authorizer = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "refs": {"api-access": restrictions},
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
                "deny": {},
            }
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == restrictions

    def test_missing_ref(self, jwt_partial_payload: dict, caplog: LogCaptureFixture) -> None:
        authorizer = self._make_mocked_authorizer(
            {
                **jwt_partial_payload,
                "allow": {"test_resource": {"permission_name": {"ref": "api-access"}}},
                "deny": {},
            }
        )

        with pytest.raises(PermissionDenied):
            authorizer.check_access()

        assert authorizer.outcome == DENY
        assert caplog.record_tuples == [
            ("lbz.authz.authorizer", logging.ERROR, 'Missing "api-access" ref in the policy')
        ]

    def test_sign_authz(self) -> None:
        token = Authorizer.sign_authz({"allow": {ALL: ALL}, "deny": {}}, SAMPLE_PRIVATE_KEY)
        assert token == EXPECTED_TOKEN

    def test_sign_authz_not_a_dict_error(self) -> None:
        with pytest.raises(ValueError, match="private_key_jwk must be a jwk dict"):
            Authorizer.sign_authz({}, private_key_jwk="")

    def test_sign_authz_no_kid_error(self) -> None:
        with pytest.raises(ValueError, match="private_key_jwk must have the 'kid' field"):
            Authorizer.sign_authz({}, private_key_jwk={})
