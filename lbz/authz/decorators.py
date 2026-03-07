from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from lbz.authz.utils import check_permission
from lbz.collector import authz_collector
from lbz.resource import Resource

P = ParamSpec("P")
R = TypeVar("R")

S = TypeVar("S", bound=Resource)


def authorization(permission_name: str | None = None) -> Callable[
    [Callable[Concatenate[S, P], R]],
    Callable[Concatenate[S, P], R],
]:
    """Wrapper for easy adding authorization requirement."""

    def decorator(function: Callable[Concatenate[S, P], R]) -> Callable[Concatenate[S, P], R]:
        # to consider adding more abstraction with 0.4 and doing it per Resource
        # on this stage `func` is a function not a method as class was not yet fully created
        # Useful link https://stackoverflow.com/questions/3589311
        authz_collector.add_authz(permission_name or function.__name__)

        @wraps(function)
        def wrapped(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
            kwargs["restrictions"] = check_permission(self, permission_name or function.__name__)
            return function(self, *args, **kwargs)

        return wrapped

    return decorator
