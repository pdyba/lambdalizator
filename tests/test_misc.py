#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access, too-few-public-methods
from collections.abc import MutableMapping

from lbz.misc import MultiDict, NestedDict, Singleton, error_catcher, get_logger


def test_nested_dict():
    nest = NestedDict()
    nest["a"]["b"]["c"]["d"]["e"] = "z"
    assert nest == {"a": {"b": {"c": {"d": {"e": "z"}}}}}


def test_singleton():
    class AClass(metaclass=Singleton):
        pass

    a_inst = AClass()
    b_inst = AClass()
    c_inst = AClass()
    assert a_inst == b_inst == c_inst
    assert Singleton._instances[AClass] == a_inst
    a_inst._del()
    assert Singleton._instances.get(AClass) is None


def test_multi_dict():
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
    a_loger = get_logger("a")
    b_loger = get_logger("b")
    assert a_loger != b_loger
    try:
        raise ZeroDivisionError
    except ZeroDivisionError as err:
        a_loger.exception(err)
        assert "Traceback" in caplog.text
        assert "ZeroDivisionError" in caplog.text


def test_error_catcher(caplog):
    @error_catcher
    def zero_division():
        return 2 / 0

    zero_division()
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text


def test_error_catcher_class(caplog):
    class AClass:
        logger = get_logger("xxxxx")

        @error_catcher
        def zero_division(self):
            return 2 / 0

    AClass().zero_division()
    assert "xxxxx" in caplog.text
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text
