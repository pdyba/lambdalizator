# coding=utf-8
"""
Authorization helper wrappers (decorators).
"""
from functools import wraps
from typing import Callable, Any

from lbz.authz.utils import check_permission
from lbz.collector import authz_collector
from lbz.resource import Resource


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
