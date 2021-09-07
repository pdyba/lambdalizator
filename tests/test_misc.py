# coding=utf-8
from collections.abc import MutableMapping

import pytest

from lbz.misc import MultiDict, NestedDict, Singleton, error_catcher, get_logger


def test_nested_dict() -> None:
    nest = NestedDict()
    nest["a"]["b"]["c"]["d"]["e"] = "z"
    assert nest == {"a": {"b": {"c": {"d": {"e": "z"}}}}}
    assert nest["a"]["b"]["c"]["d"]["e"] == "z"


def test_singleton() -> None:
    class AClass(metaclass=Singleton):
        pass

    a_inst = AClass()
    b_inst = AClass()
    c_inst = AClass()
    assert a_inst is b_inst is c_inst
    assert Singleton._instances[AClass] == a_inst  # pylint: disable=protected-access
    a_inst._del()  # pylint: disable=protected-access
    assert Singleton._instances.get(AClass) is None  # pylint: disable=protected-access


def test_multi_dict() -> None:
    assert issubclass(MultiDict, MutableMapping)
    multi_dict = MultiDict({"a": ["a", "b", "c"]})
    assert multi_dict["a"] == "c"
    assert multi_dict.get("a") == "c"
    assert multi_dict.getlist("a") == ["a", "b", "c"]
    assert multi_dict.original_items() == [("a", ["a", "b", "c"])]

    del multi_dict["a"]
    assert multi_dict.get("a") is None
    assert multi_dict.__repr__() == str(multi_dict)
    assert str(multi_dict) == "MultiDict({})"
    multi_dict["b"] = "abc"
    for letter in multi_dict:
        assert letter == "b"
    assert len(multi_dict) == 1
    assert multi_dict.getlist("b") == ["abc"]
    assert multi_dict.original_items() == [("b", ["abc"])]


def test_multi_dict_init_empty() -> None:
    multi_dict = MultiDict(None)
    assert multi_dict._dict == {}  # pylint: disable=protected-access


def test_multi_dict_index_error() -> None:
    multi_dict = MultiDict({"a": []})
    with pytest.raises(KeyError):
        multi_dict["a"]  # pylint: disable=pointless-statement


def test_get_logger(caplog) -> None:
    a_loger = get_logger("a")
    b_loger = get_logger("b")
    assert a_loger != b_loger
    try:
        raise ZeroDivisionError
    except ZeroDivisionError as err:
        a_loger.exception(err)
        assert "Traceback" in caplog.text
        assert "ZeroDivisionError" in caplog.text


def test_error_catcher(caplog) -> None:
    @error_catcher
    def zero_division() -> None:
        return 2 / 0

    zero_division()
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text


def test_error_catcher_class(caplog) -> None:
    class AClass:
        logger = get_logger("xxxxx")

        @error_catcher
        def zero_division(self) -> None:
            return 2 / 0

    AClass().zero_division()
    assert "xxxxx" in caplog.text
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text
