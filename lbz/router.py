# coding=utf-8
"""
Router module.
"""
import json
from functools import wraps

from lbz.misc import NestedDict, Singleton


class Router(metaclass=Singleton):
    """
    Router Class.
    """

    def __init__(self):
        self._routes = NestedDict()

    def __getitem__(self, route):
        return self._routes[route]

    def __str__(self):
        return json.dumps(self._routes, indent=4)

    def __repr__(self):
        return self.__str__()

    def __contains__(self, *args, **kwargs):
        return self._routes.__contains__(*args, **kwargs)

    def __len__(self):
        return len(self._routes)

    def __iter__(self):
        return self._routes.__iter__()

    def add_route(self, routes, method, handler):
        """
        Registers handler to route and method.
        """
        self._routes[routes][method] = handler


def add_route(route, method="GET"):
    """
    Flask-like wrapper for adding routes.
    """

    def wrapper(func):
        router = Router()
        router.add_route(route, method, func.__name__)

        @wraps(func)
        def wrapped(self, *func_args, **func_kwargs):
            return func(self, *func_args, **func_kwargs)

        return wrapped

    return wrapper
