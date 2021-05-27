#!/usr/local/bin/python3.8
# coding=utf-8
from collections.abc import MutableMapping

from lbz.misc import MultiDict, NestedDict, Singleton, get_logger


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
    multi_dict = MultiDict({"a": ["a", "b", "c"]})
    assert multi_dict["a"] == "c"
    assert multi_dict.get("a") == "c"
    assert multi_dict.getlist("a") == ["a", "b", "c"]

    del multi_dict["a"]
    assert multi_dict.get("a") is None
    assert multi_dict.__repr__() == str(multi_dict)
    assert str(multi_dict) == "MultiDict({})"
    multi_dict["b"] = "abc"
    for letter in multi_dict:
        assert letter == "b"
    assert len(multi_dict) == 1
    assert multi_dict.getlist("b") == ["abc"]


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
