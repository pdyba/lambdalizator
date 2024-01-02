import json
from collections.abc import Callable, Iterator
from functools import wraps
from typing import Any

from lbz.misc import NestedDict, Singleton


class Router(metaclass=Singleton):
    def __init__(self) -> None:
        self._routes = NestedDict()

    def __getitem__(self, route: str) -> Any:
        return self._routes[route]

    def __str__(self) -> str:
        return json.dumps(self._routes, indent=4)

    def __repr__(self) -> str:
        return self.__str__()

    def __contains__(self, o: Any) -> bool:
        return self._routes.__contains__(o)

    def __len__(self) -> int:
        return len(self._routes)

    def __iter__(self) -> Iterator:
        return self._routes.__iter__()

    def add_route(self, route: str, method: str, handler: str) -> None:
        """Registers handler to route and method."""
        self._routes[route][method] = handler

    def clear(self) -> None:
        self._routes = NestedDict()


def add_route(route: str, method: str = "GET") -> Callable:
    """Flask-like wrapper for adding routes."""

    def wrapper(func: Callable) -> Callable:
        router = Router()
        router.add_route(route, method, func.__name__)

        @wraps(func)
        def wrapped(self: Any, *func_args: Any, **func_kwargs: Any) -> Any:
            return func(self, *func_args, **func_kwargs)

        return wrapped

    return wrapper
