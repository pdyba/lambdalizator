# coding=utf-8
"""
Misc Helpers of Lambda Framework.
"""
import copy
import logging
import logging.handlers
from collections.abc import MutableMapping
from functools import wraps
from os import environ
from typing import Any, Callable, Hashable, Iterator, Optional, List, Iterable

LOGGING_LEVEL = environ.get("LOGGING_LEVEL", "INFO")


class NestedDict(dict):
    """
    Endless nested dict.
    """

    def __getitem__(self, key: str) -> Any:
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

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        def _del(a_cls: Any) -> None:
            """Enables deletion of singletons"""
            del Singleton._instances[a_cls._cls_name]  # pylint: disable=protected-access

        if cls not in cls._instances:
            cls._del = _del
            cls._cls_name = cls
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MultiDict(MutableMapping):
    """
    Advanced Multi Dictionary.
    """

    def __init__(self, mapping: Optional[dict]):
        if mapping is None:
            mapping = {}

        self._dict = mapping

    def __getitem__(self, k: Hashable) -> Any:
        try:
            return self._dict[k][-1]
        except IndexError as error:
            raise KeyError(k) from error

    def __setitem__(self, k: Hashable, v: Any) -> None:
        self._dict[k] = [v]

    def __delitem__(self, k: Hashable) -> None:
        del self._dict[k]

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator:
        return iter(self._dict)

    def __repr__(self) -> str:
        return "MultiDict(%s)" % self._dict

    def __str__(self) -> str:
        return repr(self)

    def getlist(self, k: Hashable) -> list:
        """
        Returns a list of all values for specific key.
        """
        return list(self._dict[k])

    def original_items(self, keys_to_skip: Iterable[Hashable] = None) -> List[tuple]:
        keys_to_skip = keys_to_skip or []
        return [(key, values) for key, values in self._dict.items() if key not in keys_to_skip]


def get_logger(name: str) -> logging.Logger:
    """Shortcut for creating logger instance."""
    logger_obj = logging.getLogger(name)
    logger_obj.setLevel(logging.getLevelName(LOGGING_LEVEL))
    return logger_obj


logger = get_logger(__name__)


def error_catcher(function: Callable, default_return: Any = False) -> Callable:
    """
    Universal Error Catcher
    """

    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Exception as error:  # pylint: disable=broad-except
            if len(args) > 0 and hasattr(args[0], "logger"):
                args[0].logger.exception(error)
            else:
                logger.exception(error)
            return default_return

    return wrapped


def deep_update(dict_to_update: dict, update_data: dict) -> None:
    """Recursively updates keys in the first dict with the data in the second dict."""
    for key, value in update_data.items():
        if key in dict_to_update:
            if isinstance(value, dict):
                deep_update(dict_to_update[key], value)
                continue
        dict_to_update[key] = copy.deepcopy(value)


def is_in_debug_mode() -> bool:
    return environ.get("LBZ_DEBUG_MODE", "").lower() == "true"
