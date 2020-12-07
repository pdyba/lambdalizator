#!/usr/local/bin/python3.8
# coding=utf-8
"""
Authorizer.
"""
import json
import warnings
from functools import wraps
from os import environ

from jose import jwt

from lbz.exceptions import PermissionDenied, NotAcceptable, SecurityRiskWarning
from lbz.jwt_utils import decode_jwt
from lbz.misc import NestedDict, Singleton

EXPIRATION_KEY = environ.get("EXPIRATION_KEY", "exp")
ALLOWED_ISS = environ.get("ALLOWED_ISS")


RESTRICTED = ["*", "self"]
ALL = "*"
ALLOW = 1
DENY = 0
LIMITED_ALLOW = -1


class Authorizer(metaclass=Singleton):
    allow = {}
    deny = {}
    action = None
    outcome = None
    allowed_resource = None
    denied_resource = None
    expiration = None
    iss = None

    def __init__(self, resource=None):
        self.resource = resource
        self._permissions = NestedDict()

    def __getitem__(self, y):
        return self._permissions[y]

    def __str__(self):
        return json.dumps({self.resource: self._permissions})

    def __repr__(self):
        return self.__str__()

    def __contains__(self, *args, **kwargs):
        return self._permissions.__contains__(*args, **kwargs)

    def __len__(self):
        return len(self._permissions)

    def __iter__(self):
        return self._permissions.__iter__()

    def add_permission(self, permission_name, function):
        self._permissions[function] = permission_name

    def set_resource(self, resource_name):
        self.resource = resource_name

    def validate(self, function_name):
        if function_name not in self._permissions:
            raise NotAcceptable()
        if self.expiration is None:
            warnings.warn(
                "EXPIRATION_KEY will be mandatory with 0.2 please upgrade Authz provider",
                DeprecationWarning,
            )
        if self.iss is None:
            warnings.warn(
                "Lack ALLOWED_ISS is a security risk You should add it.",
                SecurityRiskWarning,
            )
        elif self.iss and self.iss != ALLOWED_ISS:
            raise PermissionDenied(f"{self.iss} is not allowed token issuer")
        self.set_initial_state(function_name)
        if self.deny:
            self._check_deny()
        self._check_allow()
        if self.denied_resource and self.outcome:
            self.outcome = LIMITED_ALLOW
        if self.outcome == DENY:
            raise PermissionDenied

    def set_initial_state(self, function_name: str) -> None:
        self.outcome = DENY
        self.action = self._permissions[function_name]

    def set_policy(self, token: str):
        policy = decode_jwt(token)
        self.allow = policy["allow"]
        self.deny = policy["deny"]
        self.expiration = policy.get(EXPIRATION_KEY)
        self.iss = policy.get("iss")
        self.outcome = DENY
        self.allowed_resource = None
        self.denied_resource = None

    def reset_policy(self):
        self.allow = {}
        self.deny = {}
        self.expiration = None
        self.iss = None
        self.outcome = DENY
        self.allowed_resource = None
        self.denied_resource = None

    def _deny_if_all(self, permission):
        if permission == ALL:
            raise PermissionDenied(
                f"You don't have permission to {self.action} on {self.resource}"
            )

    def _check_deny(self):
        self._deny_if_all(self.deny.get("*", self.allow.get(self.resource)))
        if d_domain := self.deny.get(self.resource):
            self._deny_if_all(d_domain)
            if resource := d_domain.get(self.action):
                self.check_resource(resource)
                self.denied_resource = resource

    def check_resource(self, resource):
        self._deny_if_all(resource)
        if isinstance(resource, dict):
            for k, v in resource.items():
                self._deny_if_all(k)
                self._deny_if_all(v)

    def _allow_if_allow_all(self, permission):
        if permission == ALL:
            self.outcome = ALLOW
            self.allowed_resource = ALL
            return True

    def _check_allow(self):
        if not self.allow:
            raise PermissionDenied
        elif self._allow_if_allow_all(self.allow) or self._allow_if_allow_all(
            self.allow.get("*", self.allow.get(self.resource))
        ):
            return
        elif self.allow:
            if d_domain := self.allow.get(self.resource):
                if self._allow_if_allow_all(d_domain):
                    return
                elif resource_to_check := d_domain.get(self.action):
                    self.outcome = ALLOW
                    self.allowed_resource = resource_to_check.get("allow")
                    self.denied_resource = resource_to_check.get("deny")

    def get_restrictions(self) -> dict:
        return {"allow": self.allowed_resource, "deny": self.denied_resource}

    @staticmethod
    def sign_authz(authz_data: dict, private_key_jwk: dict) -> str:
        if not isinstance(private_key_jwk, dict):
            raise ValueError("private_key_jwk must be a jwk dict")
        if "kid" not in private_key_jwk:
            raise ValueError("private_key_jwk must have the 'kid' field")

        return jwt.encode(
            authz_data, private_key_jwk, algorithm="RS256", headers={"kid": private_key_jwk["kid"]}
        )


def add_authz(permission_name=""):
    def wrapper(func):
        Authorizer().add_permission(permission_name or func.__name__, func.__name__)
        return func

    return wrapper


def authorize(func):
    @wraps(func)
    def wrapped(self, *func_args, **func_kwargs):
        self._authorizer.validate(func.__name__)
        limited_permissions = self._authorizer.get_restrictions()
        return func(self, *func_args, **func_kwargs, restrictions=limited_permissions)

    return wrapped


def set_authz(cls):
    cls._authorizer.set_resource(cls._name or cls.__name__.lower())
    return cls
