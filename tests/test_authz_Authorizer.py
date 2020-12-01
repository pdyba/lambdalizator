#!/usr/local/bin/python3.8
# coding=utf-8
from datetime import datetime, timedelta
import random
import string

import pytest

from lbz.authz import Authorizer, ALL, ALLOW, DENY, LIMITED_ALLOW
from lbz.exceptions import PermissionDenied, NotAcceptable, SecurityRiskWarning, Unauthorized
from lbz.misc import NestedDict


class TestAuthorizerInit:
    def setup_class(self):
        self.authz = Authorizer(resource="res")
        self.authz._del()

    def setup_method(self, test_method):
        self.authz = Authorizer(resource="res")

    def teardown_method(self, test_method):
        self.authz._del()

    def test__init__(self):
        """
        Explist testing without data.
        :return:
        """
        assert self.authz.allow == {}
        assert self.authz.deny == {}
        assert self.authz.action is None
        assert self.authz.outcome is None
        assert self.authz.allowed_resource is None
        assert self.authz.allowed_resource is None
        assert self.authz.resource == "res"
        assert isinstance(self.authz._permissions, NestedDict)


class TestAuthorizer:
    def setup_class(self):
        self.authz = Authorizer(resource="res")
        self.authz._del()

    def setup_method(self, method):
        self.authz = Authorizer(resource="res")
        self.authz.add_permission("permission_name", "function_name")
        self.iat = int(datetime.utcnow().timestamp())
        self.exp = int((datetime.utcnow() + timedelta(hours=6)).timestamp())
        self.iss = "test"
        token = self.authz.sign_authz(
            {
                "allow": {ALL: ALL},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)

    def teardown_method(self, method):
        self.authz._del()

    def test__init__(self):
        """
        Explicit testing without data.
        :return:
        """
        assert self.authz.allow == {ALL: ALL}
        assert self.authz.deny == {}
        assert self.authz.action is None
        assert self.authz.outcome == DENY
        assert self.authz.allowed_resource is None
        assert self.authz.allowed_resource is None
        assert self.authz.resource == "res"
        assert isinstance(self.authz._permissions, NestedDict)

    def test__getitem__(self):
        assert self.authz["function_name"] == "permission_name"

    def test__str__(self):
        assert str(self.authz) == '{"res": {"function_name": "permission_name"}}'

    def test__repr__(self):
        assert str(self.authz) == '{"res": {"function_name": "permission_name"}}'

    def test__contains__(self):
        assert "function_name" in self.authz

    def test__len__(self):
        assert len(self.authz) == 1

    def test__iter__(self):
        acc = 0
        for x in self.authz:
            acc += 1
        assert acc == 1

    def test_add_permission(self):
        self.authz.add_permission("permission_name_2", "function_name_2")
        assert self.authz["function_name_2"] == "permission_name_2"

    def test_set_resource(self):
        self.authz.set_resource("new_res")
        assert self.authz.resource == "new_res"

    def test_set_initial_state(self):
        self.authz.outcome = random.choice((ALLOW, LIMITED_ALLOW))
        self.authz.action = "".join(random.choices(string.ascii_letters, k=10))
        self.authz.add_permission("initial_permission", "initial_function")
        self.authz.set_initial_state("initial_function")
        assert self.authz.outcome == DENY
        assert self.authz.action == "initial_permission"

    def test_validate_all(self):
        self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW

    def test_validate_fail_all(self):
        token = self.authz.sign_authz(
            {
                "allow": {},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)
        with pytest.raises(PermissionDenied):
            self.authz.validate("function_name")
        assert self.authz.outcome == DENY

    def test_wrong_iss(self):
        token = self.authz.sign_authz(
            {
                "allow": {},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": "test2",
            }
        )
        self.authz.set_policy(token)
        with pytest.raises(PermissionDenied):
            self.authz.validate("function_name")
        assert self.authz.outcome == DENY

    def test_validate_one(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": ALL}}},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)
        self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW

    def test_validate_one_deprecation(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": ALL}}},
                "deny": {},
            }
        )
        self.authz.set_policy(token)
        with pytest.warns(DeprecationWarning):
            self.authz.validate("function_name")
        with pytest.warns(SecurityRiskWarning):
            self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW

    def test_validate_one_with_expiration(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": ALL}}},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)
        self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW

    def test_validate_one_with_expired(self):
        expiration_negative = int((datetime.utcnow() + timedelta(seconds=1)).timestamp())
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": ALL}}},
                "deny": {},
                "exp": expiration_negative,
                "iat": self.iat,
                "iss": self.iss,
            }
        )

        with pytest.raises(Unauthorized):
            self.authz.set_policy(token)
        assert self.authz.outcome == DENY

    def test_validate_one_scope(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": "self"}}},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)
        self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == "self"

    def test_validate_fail_one_scope(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"deny": "self"}}},
                "deny": {},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)
        self.authz.validate("function_name")
        assert self.authz.outcome == LIMITED_ALLOW
        assert self.authz.denied_resource == "self"

    def test_validate_raises_not_acceptable(self):
        with pytest.raises(NotAcceptable):
            self.authz.validate("function_no_name")

    def test_set_policy(self):
        token = self.authz.sign_authz(
            {
                "allow": {},
                "deny": {ALL: ALL},
                "exp": self.exp,
                "iat": self.iat,
                "iss": self.iss,
            }
        )
        self.authz.set_policy(token)
        assert self.authz.allow == {}
        assert self.authz.deny == {ALL: ALL}

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
        self.authz.action = "permission_name"
        with pytest.raises(PermissionDenied):
            self.authz._check_deny()
        assert self.authz.outcome == DENY

    def test_check_deny_one_scope(self):
        self.authz.deny = {"res": {"permission_name": "self"}}
        self.authz.action = "permission_name"
        self.authz._check_deny()
        assert self.authz.denied_resource == "self"

    def test_allow_if_all(self):
        assert self.authz._allow_if_allow_all(ALL)
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == ALL

    def test_check_allow_all(self):
        self.authz._check_allow()
        assert self.authz.outcome == ALLOW

    def test_check_allow_fail_all(self):
        self.authz.allow = None
        with pytest.raises(PermissionDenied):
            self.authz._check_allow()
            assert self.authz.outcome == ALLOW

    def test_check_allow_one(self):
        self.authz.allow = {"res": {"permission_name": {"allow": ALL}}}
        self.authz.action = "permission_name"
        self.authz._check_allow()
        assert self.authz.outcome == ALLOW

    def test_check_allow_one_scope(self):
        self.authz.allow = {"res": {"permission_name": {"allow": "self"}}}
        self.authz.action = "permission_name"
        self.authz._check_allow()
        assert self.authz.outcome == ALLOW
        assert self.authz.allowed_resource == "self"

    def test_check_allow_fail_one_scope(self):
        self.authz.allow = {"res": {"permission_name": {"deny": "self"}}}
        self.authz.action = "permission_name"
        self.authz._check_allow()
        assert self.authz.outcome == ALLOW
        assert self.authz.denied_resource == "self"

    def test_get_restrictions_restricted(self):
        self.authz.allowed_resource = ALL
        self.authz.denied_resource = {"city": "warszawa"}
        assert self.authz.get_restrictions() == {
            "allow": ALL,
            "deny": {"city": "warszawa"},
        }, self.authz.get_restrictions()

    def test_sign_authz(self):
        # noqa: E501
        token = self.authz.sign_authz({"allow": {ALL: ALL}, "deny": {}})
        assert (
            token
            == "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk0OTRhZDc1LTNmNTQtNDE1NS04NGZhLWMxYTE3ZGEyMmIzNSIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.nDqCxO2Q1iXpxzbH7syxuyqw7kCY0sDfi9RX-VSUMTRN5aWTLt1bcPw4oN_jx89-YHBzDwnwBc07RsMgpFuo4zz2LU9PF0ciYxMNX-atTNsaIn05NkXT08au2AYb0DRCDS76MZ4QNi-4mRpLrj1SD4mSCwGtc2WNw9f0J0Vm4ZCYPVW6BqpcHcaFXzcFZ6EIoooaK6GvdTOjy498lWsAXjAen2U6Jles_BwFjqW1lW_ky4WV4J9NnK3v5wWKgR1Pg4R4LpnhIXe0dU_l64JHoJA3YcYxl-qilHfoBduc3La4kRKk7FAQDIqbOv4uN03BIoDXLH5t2uJ1Sm79Pe0ngGd5pSBmfUDKOGsHtx_3_9ZKfp-E2IVS0C7r36p4Ue0gKQzn0pXxa591bxm_puJAQ399SdbmlOJsM2cVFYAtlUQvWgErc57WcUJ0Qe4jEycury7hagNbP2fLn-7Gg4gZHiZ_Ul7L6GukbDfCHnhxSS4P3t3cVtWuslZi16hDhNbOTKD95y7PXvHePvI57ALV2v0RecQ5Blwurt1OuDRSjCYXyO6U4Y9MBHcd1wMtDoVW0jjvjXvqkEhuB52Zajh_yTNnJo0OAHpuK5wldVpECGFVx1rkW1ypKqlukGIgD--m6ElKnl6jw5VWSbdh2TJsZHnzjovbQUeqZOeMxwX6SE8"
            # noqa: E501
        )

    def test_decode_authz(self):
        token = self.authz.decode_authz(
            "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk0OTRhZDc1LTNmNTQtNDE1NS04NGZhLWMxYTE3ZGEyMmIzNSIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.nDqCxO2Q1iXpxzbH7syxuyqw7kCY0sDfi9RX-VSUMTRN5aWTLt1bcPw4oN_jx89-YHBzDwnwBc07RsMgpFuo4zz2LU9PF0ciYxMNX-atTNsaIn05NkXT08au2AYb0DRCDS76MZ4QNi-4mRpLrj1SD4mSCwGtc2WNw9f0J0Vm4ZCYPVW6BqpcHcaFXzcFZ6EIoooaK6GvdTOjy498lWsAXjAen2U6Jles_BwFjqW1lW_ky4WV4J9NnK3v5wWKgR1Pg4R4LpnhIXe0dU_l64JHoJA3YcYxl-qilHfoBduc3La4kRKk7FAQDIqbOv4uN03BIoDXLH5t2uJ1Sm79Pe0ngGd5pSBmfUDKOGsHtx_3_9ZKfp-E2IVS0C7r36p4Ue0gKQzn0pXxa591bxm_puJAQ399SdbmlOJsM2cVFYAtlUQvWgErc57WcUJ0Qe4jEycury7hagNbP2fLn-7Gg4gZHiZ_Ul7L6GukbDfCHnhxSS4P3t3cVtWuslZi16hDhNbOTKD95y7PXvHePvI57ALV2v0RecQ5Blwurt1OuDRSjCYXyO6U4Y9MBHcd1wMtDoVW0jjvjXvqkEhuB52Zajh_yTNnJo0OAHpuK5wldVpECGFVx1rkW1ypKqlukGIgD--m6ElKnl6jw5VWSbdh2TJsZHnzjovbQUeqZOeMxwX6SE8"
            # noqa: E501, W505
        )
        assert token == {"allow": {ALL: ALL}, "deny": {}}
