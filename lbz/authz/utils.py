# coding=utf-8
"""
Authorization helper functions.
"""
from lbz.authz.authorizer import Authorizer
from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.resource import Resource


def check_permission(resource: Resource, permission_name: str) -> dict:
    """
    Check if requester has sufficient permissions to do something on specific resource.

    Raises if not.
    """
    base_permission_policy = resource.get_guest_authorization()
    if (authorization_header := resource.request.headers.get("Authorization")) is None:
        if not base_permission_policy:
            raise Unauthorized("Authorization header missing or empty")

    authorizer = Authorizer(
        auth_jwt=authorization_header,
        resource_name=resource.get_name(),
        permission_name=permission_name,
        base_permission_policy=base_permission_policy,
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
