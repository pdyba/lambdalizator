#!/usr/local/bin/python3.8
# coding=utf-8
"""
Misc Helpers of Lambda Framework.
"""
from collections.abc import MutableMapping
from functools import wraps
from os import environ

import logging
import logging.handlers
import traceback

LOGGING_LEVEL = environ.get("LOGGING_LEVEL", "INFO")


class NestedDict(dict):
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return self.setdefault(key, NestedDict())


class Singleton(type):
    """
    Usage:
        class MyClass(metaclass=Singleton):
            pass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        def _del(cls):
            """Enables deletion of singletons"""
            del Singleton._instances[cls._cls_name]

        if cls not in cls._instances:
            cls._del = _del
            cls._cls_name = cls
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MultiDict(MutableMapping):  # pylint: disable=too-many-ancestors
    def __init__(self, mapping):
        if mapping is None:
            mapping = {}

        self._dict = mapping

    def __getitem__(self, k):
        try:
            return self._dict[k][-1]
        except IndexError:
            raise KeyError(k)

    def __setitem__(self, k, v):
        self._dict[k] = [v]

    def __delitem__(self, k):
        del self._dict[k]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __repr__(self):
        return "MultiDict(%s)" % self._dict

    def __str__(self):
        return repr(self)

    def getlist(self, k):
        return list(self._dict[k])


def get_logger(name: str):
    """
    Setting options for logger
    """
    logger_obj = logging.getLogger(name)
    logger_obj.setLevel(logging.getLevelName(LOGGING_LEVEL))

    def format_error(error):
        logger_obj.error("\n{}\nTraceback: {}".format(error, traceback.format_exc()))

    logger_obj.format_error = format_error
    return logger_obj


logger = get_logger(__name__)


def error_catcher(function, default_return=False):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            if len(args) > 0 and hasattr(args[0], "logger"):
                args[0].logger.format_error(error)
            else:
                logger.format_error(error)
            return default_return

    return wrapped
