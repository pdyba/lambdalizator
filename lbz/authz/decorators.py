# coding=utf-8
"""
Authorization helper wrappers (decorators).
"""
from functools import wraps
from typing import Callable, Any

from lbz.authz.authorizer import Authorizer
from lbz.collector import authz_collector
from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.resource import Resource


def check_permission(resource: Resource, permission_name: str) -> dict:
    """
    Check if requester has sufficient permissions to do something on specific resource.

    Raises if not.
    """
    guest_authorization_policy = None
    if not (authorization_header := resource.request.headers.get("Authorization", "")):
        if not (guest_authorization_policy := resource.get_guest_authorization()):
            raise Unauthorized("Authorization header missing or empty")

    authorizer = Authorizer(
        auth_jwt=authorization_header,
        resource_name=resource.get_name(),
        permission_name=permission_name,
        policy_override=guest_authorization_policy,
    )
    authorizer.check_access()
    return authorizer.restrictions


def has_permission(resource: Resource, permission_name: str) -> bool:
    """
    Safe Check if requester has sufficient permissions to do something on specific resource.

    Does not raise.
    """
    try:
        check_permission(resource, permission_name)
    except (Unauthorized, PermissionDenied):
        return False
    return True


def authorization(permission_name: str = None) -> Callable:
    """
    Wrapper for easy adding authorization requirement.
    """

    def decorator(func: Callable) -> Callable:
        # to consider adding more abstraction with 0.4 and doing it per Resource
        # on this stage `func` is a function not a method as class was not yet fully created
        # Useful link https://stackoverflow.com/questions/3589311
        authz_collector.add_authz(permission_name or func.__name__)

        @wraps(func)
        def wrapped(self: Resource, *args: Any, **kwargs: Any) -> Any:

            restrictions = check_permission(self, permission_name or func.__name__)
            return func(self, *args, restrictions=restrictions, **kwargs)

        return wrapped

    return decorator
