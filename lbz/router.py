import json
from collections.abc import Callable, Iterator
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from lbz.misc import NestedDict, Singleton

P = ParamSpec("P")
R = TypeVar("R")


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


def add_route(route: str, method: str = "GET") -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Flask-like wrapper for adding routes."""

    def wrapper(function: Callable[P, R]) -> Callable[P, R]:
        router = Router()
        router.add_route(route, method, function.__name__)

        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            return function(*args, **kwargs)

        return wrapped

    return wrapper
