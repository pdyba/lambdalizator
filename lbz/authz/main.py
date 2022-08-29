from types import SimpleNamespace
from typing import Any, Collection, Dict, Optional, Set, Union

from lbz.authentication import User
from lbz.authz.authorizer import ALL
from lbz.exceptions import PermissionDenied
from lbz.misc import get_logger

logger = get_logger(__name__)


class AuthHelper:
    def __init__(self, user: Optional[User], restrictions: dict) -> None:
        self.user: Optional[User] = user
        self.restrictions: dict = restrictions
        self.allowed_values_map: Dict[str, Set] = {}
        self.denied_values_map: Dict[str, Set] = {}

        allow = restrictions.get("allow") or {}
        deny = restrictions.get("deny") or {}

        if not allow:
            logger.warning("Auth policy with empty allow")
            raise PermissionDenied
        if allow == ALL:
            allow = {}

        for field, allowed_values in allow.items():
            self.allowed_values_map[field] = self._values_to_set(allowed_values)
        for field, denied_values in deny.items():
            self.denied_values_map[field] = self._values_to_set(denied_values)

    def check_access_to(self, obj: Any) -> None:
        if isinstance(obj, dict):
            obj = SimpleNamespace(**obj)

        for field, allowed_values in self.allowed_values_map.items():
            if not hasattr(obj, field) or getattr(obj, field) not in allowed_values:
                raise PermissionDenied

        for field, denied_values in self.denied_values_map.items():
            if hasattr(obj, field) and getattr(obj, field) in denied_values:
                raise PermissionDenied

    def check_access_to_all(self, objs: Collection) -> None:
        for obj in objs:
            self.check_access_to(obj)

    @staticmethod
    def _to_set(values: Union[None, str, list]) -> set:
        return set(values) if isinstance(values, list) else {values}

    def _values_to_set(self, values: Union[None, str, list]) -> set:
        values_set = self._to_set(values)
        # TODO: [SCRUM-1906] Recognize partner_id the same way as the "self" value
        if "self" in values_set:
            if not self.user:
                raise PermissionDenied
            values_set.remove("self")
            values_set.add(self.user.username)
        return values_set
