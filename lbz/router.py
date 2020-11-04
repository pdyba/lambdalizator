#!/usr/local/bin/python3.8
# coding=utf-8
"""
Router.
"""
import json

from functools import wraps

from lbz.misc import NestedDict, Singleton


class Router(metaclass=Singleton):
    def __init__(self):
        self._routes = NestedDict()

    def __getitem__(self, y):
        return self._routes[y]

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
        self._routes[routes][method] = handler


def add_route(route, method="GET"):
    def wrapper(func):
        router = Router()
        router.add_route(route, method, func.__name__)

        @wraps(func)
        def wrapped(self, *func_args, **func_kwargs):
            return func(self, *func_args, **func_kwargs)

        return wrapped

    return wrapper
