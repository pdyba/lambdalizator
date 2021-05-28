#!/usr/local/bin/python3.8
# coding=utf-8
import warnings
from functools import wraps
from os import environ
from typing import Callable

from jose import jwt

from lbz.exceptions import PermissionDenied, SecurityRiskWarning, Unauthorized
from lbz.jwt_utils import decode_jwt
from lbz.misc import logger
from lbz.resource import Resource

EXPIRATION_KEY = environ.get("EXPIRATION_KEY", "exp")
ALLOWED_ISS = environ.get("ALLOWED_ISS")

RESTRICTED = ["*", "self"]
ALL = "*"
ALLOW = 1
DENY = 0
LIMITED_ALLOW = -1


class Authorizer:
    def __init__(
        self, auth_jwt: str, resource_name: str, permission_name: str, policy_override: dict = None
    ):
        self.outcome = DENY
        self.allowed_resource = None
        self.denied_resource = None
        self.resource = resource_name
        self.permission = permission_name
        self.refs = {}
        self.allow = {}
        self.deny = {}
        self._set_policy(auth_jwt, policy_override)

    def __repr__(self):
        return (
            f"Authorizer(auth_jwt=<jwt>, resource_name='{self.resource}', "
            f"permission_name='{self.permission}')"
        )

    def _set_policy(self, auth_jwt: str, policy_override: dict = None):
        policy = policy_override if policy_override else decode_jwt(auth_jwt)
        self.refs = policy.get("refs", {})
        try:
            self.allow = policy["allow"]
            self.deny = policy["deny"]
        except KeyError:
            raise PermissionDenied("Invalid policy in the authorization token")

        if EXPIRATION_KEY not in policy:
            warnings.warn(
                f"The auth token doesn't have the '{EXPIRATION_KEY}' field - it will be mandatory"
                f"in the next version of Lambdalizator",
                DeprecationWarning,
            )

        issuer = policy.get("iss")
        if not issuer:
            warnings.warn(
                "The auth token doesn't have the 'iss' field - consider adding it to increase"
                "the security of your application",
                SecurityRiskWarning,
            )
        elif issuer != ALLOWED_ISS:
            raise PermissionDenied(f"{issuer} is not an allowed token issuer")

    def check_access(self):
        self.outcome = DENY

        if self.deny:
            self._check_deny()
        self._check_allow_and_set_resources()
        if self.denied_resource and self.outcome:
            self.outcome = LIMITED_ALLOW
        if self.outcome == DENY:
            raise PermissionDenied

    def _deny_if_all(self, permission):
        if permission == ALL:
            raise PermissionDenied(
                f"You don't have permission to {self.permission} on {self.resource}"
            )

    def _check_deny(self):
        self._deny_if_all(self.deny.get("*", self.allow.get(self.resource)))
        if d_domain := self.deny.get(self.resource):
            self._deny_if_all(d_domain)
            if resource := d_domain.get(self.permission):
                self._check_resource(resource)
                self.denied_resource = resource

    def _check_resource(self, resource):
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

    def _get_effective_permissions(self, permissions: dict) -> dict:
        if ref_name := permissions.get("ref"):
            if ref_name not in self.refs:
                logger.warning("Missing %s ref in the policy", ref_name)
                self.outcome = DENY
                raise PermissionDenied
            return self.refs[ref_name]

        return permissions

    def _check_allow_and_set_resources(self):
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
                elif resource_to_check := d_domain.get(self.permission):
                    self.outcome = ALLOW
                    effective_permissions = self._get_effective_permissions(resource_to_check)
                    self.allowed_resource = effective_permissions.get("allow")
                    self.denied_resource = effective_permissions.get("deny")

    @property
    def restrictions(self) -> dict:
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


def check_permission(resource: Resource, permission_name: str) -> dict:
    authorization_header = resource.request.headers.get("Authorization")
    authorization_scope = None
    if not authorization_header:
        if hasattr(resource, "get_guest_authorization"):
            authorization_scope = resource.get_guest_authorization()
        else:
            raise Unauthorized("Authorization header missing or empty")

    authorizer = Authorizer(
        auth_jwt=authorization_header,
        resource_name=getattr(resource, "_name") or resource.__class__.__name__.lower(),
        permission_name=permission_name,
        policy_override=authorization_scope,
    )
    authorizer.check_access()
    return authorizer.restrictions


def has_permission(resource: Resource, permission_name: str) -> bool:
    try:
        check_permission(resource, permission_name)
    except (Unauthorized, PermissionDenied):
        return False
    return True


def authorization(permission_name: str = None):
    def decorator(func: Callable):
        @wraps(func)
        def wrapped(self: Resource, *args, **kwargs):
            restrictions = check_permission(self, permission_name or func.__name__)
            return func(self, *args, restrictions=restrictions, **kwargs)

        return wrapped

    return decorator
