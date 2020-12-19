#!/usr/local/bin/python3.8
# coding=utf-8
from datetime import datetime, timedelta

import pytest

from lbz.authz import Authorizer, ALL, ALLOW, DENY, LIMITED_ALLOW
from lbz.exceptions import PermissionDenied, SecurityRiskWarning, Unauthorized
from tests import sample_private_key


class TestAuthorizer:
    def setup_method(self):
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

    def _make_authorizer(self, token_payload: dict) -> Authorizer:
        jwt = Authorizer.sign_authz(token_payload, sample_private_key)
        return Authorizer(jwt, "res", "permission_name")

    def test__init__(self):
        assert self.authz.allow == {ALL: ALL}
        assert self.authz.deny == {}
        assert self.authz.outcome == DENY
        assert self.authz.allowed_resource is None
        assert self.authz.allowed_resource is None
        assert self.authz.resource == "res"
        assert self.authz.permission == "permission_name"

    def test__repr__(self):
        assert (
            repr(self.authz)
            == "Authorizer(auth_jwt=<jwt>, resource_name='res', permission_name='permission_name')"
        )

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
            {**self.token_payload, "allow": {"res": {"permission_name": {"allow": ALL}}}}
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
        expiration_negative = int((datetime.utcnow() + timedelta(seconds=1)).timestamp())

        with pytest.raises(Unauthorized):
            self._make_authorizer(
                {
                    **self.token_payload,
                    "allow": {"res": {"permission_name": {"allow": ALL}}},
                    "exp": expiration_negative,
                }
            )

    def test_validate_one_scope(self):
        authorizer = self._make_authorizer(
            {**self.token_payload, "allow": {"res": {"permission_name": {"allow": "self"}}}}
        )
        authorizer.check_access()
        assert authorizer.outcome == ALLOW
        assert authorizer.restrictions == {"allow": "self", "deny": None}

    def test_validate_fail_one_scope(self):
        authorizer = self._make_authorizer(
            {**self.token_payload, "allow": {"res": {"permission_name": {"deny": "self"}}}}
        )
        authorizer.check_access()
        assert authorizer.outcome == LIMITED_ALLOW
        assert authorizer.restrictions == {"allow": None, "deny": "self"}

    def test_deny_if_all(self):
        with pytest.raises(PermissionDenied):
            self.authz._deny_if_all(ALL)

    def test_check_deny_any(self):
        self.authz.deny = {ALL: ALL}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()
        assert self.authz.outcome == DENY

    def test_check_deny_res(self):
        self.authz.deny = {"res": ALL}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()
        assert self.authz.outcome == DENY

    def test_check_deny_one(self):
        self.authz.deny = {"res": {"permission_name": ALL}}
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()
        assert self.authz.outcome == DENY

    def test_check_deny_one_scope(self):
        self.authz.deny = {"res": {"permission_name": "self"}}
        self.authz._check_deny()
        assert self.authz.denied_resource == "self"

    def test_allow_if_all(self):
        assert self.authz._allow_if_allow_all(ALL)
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == ALL

    def test_check_allow_all(self):
        self.authz._check_allow_and_set_resources()
        assert self.authz.outcome == ALLOW

    def test_check_allow_fail_all(self):
        self.authz.allow = None
        with pytest.raises(PermissionDenied):
            self.authz._check_allow_and_set_resources()
            assert self.authz.outcome == ALLOW

    def test_check_allow_one(self):
        self.authz.allow = {"res": {"permission_name": {"allow": ALL}}}
        self.authz._check_allow_and_set_resources()
        assert self.authz.outcome == ALLOW

    def test_check_allow_one_scope(self):
        self.authz.allow = {"res": {"permission_name": {"allow": "self"}}}
        self.authz._check_allow_and_set_resources()
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == "self"

    def test_check_allow_fail_one_scope(self):
        self.authz.allow = {"res": {"permission_name": {"deny": "self"}}}
        self.authz._check_allow_and_set_resources()
        assert self.authz.outcome == ALLOW
        assert self.authz.denied_resource == "self"

    def test_get_restrictions_restricted(self):
        self.authz.allowed_resource = ALL
        self.authz.denied_resource = {"city": "warszawa"}
        assert self.authz.restrictions == {"allow": ALL, "deny": {"city": "warszawa"}}

    def test_sign_authz(self):
        # noqa: E501
        token = Authorizer.sign_authz({"allow": {ALL: ALL}, "deny": {}}, sample_private_key)
        assert (
            token
            == "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk0OTRhZDc1LTNmNTQtNDE1NS04NGZhLWMxYTE3ZGEyMmIzNSIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.nDqCxO2Q1iXpxzbH7syxuyqw7kCY0sDfi9RX-VSUMTRN5aWTLt1bcPw4oN_jx89-YHBzDwnwBc07RsMgpFuo4zz2LU9PF0ciYxMNX-atTNsaIn05NkXT08au2AYb0DRCDS76MZ4QNi-4mRpLrj1SD4mSCwGtc2WNw9f0J0Vm4ZCYPVW6BqpcHcaFXzcFZ6EIoooaK6GvdTOjy498lWsAXjAen2U6Jles_BwFjqW1lW_ky4WV4J9NnK3v5wWKgR1Pg4R4LpnhIXe0dU_l64JHoJA3YcYxl-qilHfoBduc3La4kRKk7FAQDIqbOv4uN03BIoDXLH5t2uJ1Sm79Pe0ngGd5pSBmfUDKOGsHtx_3_9ZKfp-E2IVS0C7r36p4Ue0gKQzn0pXxa591bxm_puJAQ399SdbmlOJsM2cVFYAtlUQvWgErc57WcUJ0Qe4jEycury7hagNbP2fLn-7Gg4gZHiZ_Ul7L6GukbDfCHnhxSS4P3t3cVtWuslZi16hDhNbOTKD95y7PXvHePvI57ALV2v0RecQ5Blwurt1OuDRSjCYXyO6U4Y9MBHcd1wMtDoVW0jjvjXvqkEhuB52Zajh_yTNnJo0OAHpuK5wldVpECGFVx1rkW1ypKqlukGIgD--m6ElKnl6jw5VWSbdh2TJsZHnzjovbQUeqZOeMxwX6SE8"
            # noqa: E501
        )
