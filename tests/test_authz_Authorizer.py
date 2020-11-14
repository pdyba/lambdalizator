#!/usr/local/bin/python3.8
# coding=utf-8
from datetime import datetime, timedelta
import random
import string

import pytest

from lbz.authz import Authorizer, ALL, ALLOW, DENY, LIMITED_ALLOW
from lbz.exceptions import PermissionDenied, ServerError
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
        self.expiration_positive = (datetime.utcnow() + timedelta(minutes=30)).timestamp()
        self.expiration_negative = (datetime.utcnow() - timedelta(minutes=30)).timestamp()
        token = self.authz.sign_authz(
            {"allow": {ALL: ALL}, "deny": {}, "expires-at": self.expiration_positive}
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
            {"allow": {}, "deny": {}, "expires-at": self.expiration_positive}
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
                "expiration-at": self.expiration_positive,
            }
        )
        self.authz.set_policy(token)
        with pytest.warns(DeprecationWarning):
            self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW

    def test_validate_one_with_expiration(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": ALL}}},
                "deny": {},
                "expires-at": self.expiration_positive,
            }
        )
        self.authz.set_policy(token)
        self.authz.validate("function_name")
        assert self.authz.outcome == ALLOW

    def test_validate_one_with_expired(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": ALL}}},
                "deny": {},
                "expires-at": self.expiration_negative,
            }
        )
        self.authz.set_policy(token)
        with pytest.raises(PermissionDenied):
            self.authz.validate("function_name")
        assert self.authz.outcome == DENY

    def test_validate_one_scope(self):
        token = self.authz.sign_authz(
            {
                "allow": {"res": {"permission_name": {"allow": "self"}}},
                "deny": {},
                "expires-at": self.expiration_positive,
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
                "expires-at": self.expiration_positive,
            }
        )
        self.authz.set_policy(token)
        self.authz.validate("function_name")
        assert self.authz.outcome == LIMITED_ALLOW
        assert self.authz.denied_resource == "self"

    def test_validate_raise_server_error(self):
        with pytest.raises(ServerError):
            self.authz.validate("function_no_name")

    def test_set_policy(self):
        token = self.authz.sign_authz(
            {"allow": {}, "deny": {ALL: ALL}, "expires-at": self.expiration_positive}
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
            == "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.rv8AvMUIdiOqrK7CscYoxc53OgqP1L76k4xd9hBv-218EYbcU5n52Tg7rWzjsxQ_9ig18vJFjk5WeHkQsMZ_rQ"
            # noqa: E501
        )

    def test_decode_authz(self):
        token = self.authz.decode_authz(
            "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhbGxvdyI6eyIqIjoiKiJ9LCJkZW55Ijp7fX0.rv8AvMUIdiOqrK7CscYoxc53OgqP1L76k4xd9hBv-218EYbcU5n52Tg7rWzjsxQ_9ig18vJFjk5WeHkQsMZ_rQ"
            # noqa: E501, W505
        )
        assert token == {"allow": {ALL: ALL}, "deny": {}}
