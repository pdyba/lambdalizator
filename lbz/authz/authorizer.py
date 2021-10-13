from typing import Union, Dict, Optional

from jose import jwt

from lbz.exceptions import PermissionDenied
from lbz.jwt_utils import decode_jwt
from lbz.misc import get_logger, deep_update

logger = get_logger(__name__)


RESTRICTED = ["*", "self"]
ALL = "*"
ALLOW = 1
DENY = 0
LIMITED_ALLOW = -1


class Authorizer:
    """
    Authorizer class responsible for Authorization.
    """

    def __init__(
        self,
        auth_jwt: Optional[str],
        resource_name: str,
        permission_name: str,
        base_permission_policy: dict = None,
    ):
        self.outcome = DENY
        self.allowed_resource: Union[str, dict, None] = None
        self.denied_resource: Union[str, dict, None] = None
        self.resource = resource_name
        self.permission = permission_name
        self.refs: Dict[str, dict] = {}
        self.allow: dict = {}
        self.deny: dict = {}
        self._set_policy(auth_jwt, base_permission_policy)

    def __repr__(self) -> str:
        return (
            f"Authorizer(auth_jwt=<jwt>, resource_name='{self.resource}', "
            f"permission_name='{self.permission}')"
        )

    def _set_policy(self, auth_jwt: str = None, base_permission_policy: dict = None) -> None:
        policy = base_permission_policy or {}
        if auth_jwt is not None:
            deep_update(policy, decode_jwt(auth_jwt))
        self.refs = policy.get("refs", {})
        try:
            self.allow = policy["allow"]
            self.deny = policy["deny"]
        except KeyError as error:
            raise PermissionDenied("Invalid policy in the authorization token") from error

    def _raise_permission_denied(self) -> None:
        logger.debug("You don't have permission to %s on %s", self.permission, self.resource)
        raise PermissionDenied()

    def check_access(self) -> None:
        """
        Main authorization checking logic.
        """
        self.outcome = DENY

        if self.deny:
            self._check_deny()
        self._check_allow_and_set_resources()
        if self.denied_resource and self.outcome:
            self.outcome = LIMITED_ALLOW
        if self.outcome == DENY:
            self._raise_permission_denied()

    def _deny_if_all(self, permission: Union[dict, str]) -> None:
        if permission == ALL:
            self._raise_permission_denied()

    def _check_deny(self) -> None:
        self._deny_if_all(self.deny.get("*", self.allow.get(self.resource)))
        if d_domain := self.deny.get(self.resource):
            self._deny_if_all(d_domain)
            if resource := d_domain.get(self.permission):
                self._check_resource(resource)
                self.denied_resource = resource

    def _check_resource(self, resource: Union[dict, str]) -> None:
        # TODO: standardize the naming convention (resource != permission)
        self._deny_if_all(resource)
        if isinstance(resource, dict):
            for key, value in resource.items():
                self._deny_if_all(key)
                self._deny_if_all(value)

    def _allow_if_allow_all(self, permission: Union[str, dict]) -> bool:
        if permission == ALL:
            self.outcome = ALLOW
            self.allowed_resource = ALL
            return True
        return False

    def _get_effective_permissions(self, permissions: dict) -> dict:
        if ref_name := permissions.get("ref"):
            if ref_name not in self.refs:
                logger.warning("Missing %s ref in the policy", ref_name)
                self.outcome = DENY
                self._raise_permission_denied()
            return self.refs[ref_name]
        return permissions

    def _check_allow_and_set_resources(self) -> None:
        if not self.allow:
            self._raise_permission_denied()
        if self._allow_if_allow_all(self.allow) or self._allow_if_allow_all(
            self.allow.get("*", self.allow.get(self.resource))
        ):
            return
        if d_domain := self.allow.get(self.resource):
            if self._allow_if_allow_all(d_domain):
                return
            if resource_to_check := d_domain.get(self.permission):
                self.outcome = ALLOW
                effective_permissions = self._get_effective_permissions(resource_to_check)
                self.allowed_resource = effective_permissions.get("allow")
                self.denied_resource = effective_permissions.get("deny")

    @property
    def restrictions(self) -> dict:
        """
        Provides restrictions in standardised format.
        """
        return {"allow": self.allowed_resource, "deny": self.denied_resource}

    @staticmethod
    def sign_authz(authz_data: dict, private_key_jwk: dict) -> str:
        """
        Signs authorization in JWT format.
        """
        if not isinstance(private_key_jwk, dict):
            raise ValueError("private_key_jwk must be a jwk dict")
        if "kid" not in private_key_jwk:
            raise ValueError("private_key_jwk must have the 'kid' field")

        authz: str = jwt.encode(
            authz_data, private_key_jwk, algorithm="RS256", headers={"kid": private_key_jwk["kid"]}
        )
        return authz
