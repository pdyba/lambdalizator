#!/usr/local/bin/python3.8
# coding=utf-8
"""
Misc Helpers of Lambda Framework.
"""
from collections.abc import MutableMapping

from lbz.misc import NestedDict
from lbz.misc import Singleton
from lbz.misc import MultiDict
from lbz.misc import get_logger
from lbz.misc import error_catcher


def test_NestedDict():
    a = NestedDict()
    a["a"]["b"]["c"]["d"]["e"] = "z"
    assert a == {"a": {"b": {"c": {"d": {"e": "z"}}}}}


def test_Singleton():
    class A(metaclass=Singleton):
        pass

    a = A()
    b = A()
    c = A()
    assert a == b == c
    assert Singleton._instances[A] == a
    a._del()
    assert Singleton._instances.get(A) is None


def test_MultiDict():
    assert issubclass(MultiDict, MutableMapping)
    x = MultiDict(None)
    # setitem
    x["a"] = "b"
    # getitem
    assert x["a"] == "b"
    assert x.get("a") == "b"

    del x["a"]
    assert x.get("a") is None
    assert x.__repr__() == str(x)
    assert str(x) == "MultiDict({})"
    x["b"] = "abc"
    acc = 0
    for a in x:
        acc += 1
    assert acc == 1
    assert x.getlist("b") == ["abc"]


def test_get_logger(caplog):
    a = get_logger("a")
    b = get_logger("b")
    assert a != b
    try:
        raise ZeroDivisionError
    except ZeroDivisionError as err:
        a.format_error(err)
        assert "Traceback" in caplog.text
        assert "ZeroDivisionError" in caplog.text


def test_error_catcher(caplog):
    @error_catcher
    def a():
        return 2 / 0

    a()
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text


def test_error_catcher_class(caplog):
    class A:
        logger = get_logger("xxxxx")

        @error_catcher
        def a(self):
            return 2 / 0

    A().a()
    assert "xxxxx" in caplog.text
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text
