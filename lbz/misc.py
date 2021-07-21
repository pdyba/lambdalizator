# coding=utf-8
"""
Misc Helpers of Lambda Framework.
"""
import logging
import logging.handlers
from collections.abc import MutableMapping
from functools import wraps
from os import environ

LOGGING_LEVEL = environ.get("LOGGING_LEVEL", "INFO")


class NestedDict(dict):
    """
    Endless nested dict.
    """

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

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        def _del(cls):
            """Enables deletion of singletons"""
            del Singleton._instances[cls._cls_name]

        if cls not in cls._instances:
            cls._del = _del
            cls._cls_name = cls
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MultiDict(MutableMapping):
    """
    Advanced Multi Dictionary.
    """

    def __init__(self, mapping: dict):
        if mapping is None:
            mapping = {}

        self._dict = mapping

    def __getitem__(self, k):
        try:
            return self._dict[k][-1]
        except IndexError as error:
            raise KeyError(k) from error

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

    def getlist(self, k: str) -> list:
        """
        Returns a list of all values for specific key.
        """
        return list(self._dict[k])


def get_logger(name: str):
    """Shortcut for creating logger instance."""
    logger_obj = logging.getLogger(name)
    logger_obj.setLevel(logging.getLevelName(LOGGING_LEVEL))
    return logger_obj


logger = get_logger(__name__)


def error_catcher(function, default_return=False):
    """
    Universal Error Catcher
    """

    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:  # pylint: disable=broad-except
            if len(args) > 0 and hasattr(args[0], "logger"):
                args[0].logger.exception(error)
            else:
                logger.exception(error)
            return default_return

    return wrapped


def copy_without_keys(data: dict, *keys) -> dict:
    """
    Clean up dict from unwanted keys.
    """
    return {key: value for key, value in data.items() if key not in keys}
