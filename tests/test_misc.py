# coding=utf-8
from collections.abc import MutableMapping
from typing import Any

import pytest
from pytest import LogCaptureFixture

from lbz.misc import (
    MultiDict,
    NestedDict,
    Singleton,
    deep_update,
    deprecated,
    error_catcher,
    get_logger,
)


def test_nested_dict() -> None:
    nest = NestedDict()
    nest["a"]["b"]["c"]["d"]["e"] = "z"
    assert nest == {"a": {"b": {"c": {"d": {"e": "z"}}}}}


def test_singleton() -> None:
    class AClass(metaclass=Singleton):
        pass

    a_inst = AClass()
    b_inst = AClass()
    c_inst = AClass()
    assert a_inst is b_inst is c_inst
    assert Singleton._instances[AClass] == a_inst  # pylint: disable=protected-access
    a_inst._del()  # type: ignore  # pylint: disable=protected-access
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
    assert repr(multi_dict) == str(multi_dict)
    assert str(multi_dict) == "MultiDict({})"
    multi_dict["b"] = "abc"
    for letter in multi_dict:
        assert letter == "b"
    assert len(multi_dict) == 1
    assert multi_dict.getlist("b") == ["abc"]
    assert multi_dict.original_items() == [("b", ["abc"])]


def test_get_logger(caplog: LogCaptureFixture) -> None:
    a_loger = get_logger("a")
    b_loger = get_logger("b")
    assert a_loger != b_loger
    try:
        raise ZeroDivisionError
    except ZeroDivisionError as err:
        a_loger.exception(err)
        assert "Traceback" in caplog.text
        assert "ZeroDivisionError" in caplog.text


def test_error_catcher(caplog: LogCaptureFixture) -> None:
    @error_catcher
    def zero_division() -> float:
        return 2 / 0

    zero_division()
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text


def test_error_catcher_class(caplog: LogCaptureFixture) -> None:
    class AClass:
        logger = get_logger("xxxxx")

        @error_catcher
        def zero_division(self) -> float:
            return 2 / 0

    AClass().zero_division()
    assert "xxxxx" in caplog.text
    assert "Traceback" in caplog.text
    assert "ZeroDivisionError" in caplog.text


def test__deep_update__does_nothing_if_empty_data_given() -> None:
    dict_to_update = {"test1": "data1"}
    update_data: dict = {}

    deep_update(dict_to_update, update_data)

    assert dict_to_update == {"test1": "data1"}


def test__deep_update__does_recursive_updates_based_on_given_data() -> None:
    dict_to_update = {
        "test1": "data1",
        "array": ["data2", "data3"],
        "dict": {
            "test4": "data4",
            "test5": "data5",
            "nested_dict": {
                "test6": "data6",
                "nested_array": ["data7"],
            },
        },
    }
    update_data = {
        "array": ["overwritten"],
        "dict": {
            "test5": "overwritten",
            "nested_dict": {
                "nested_array": [],
            },
            "test7": "added",
        },
        "test8": "added",
    }

    deep_update(dict_to_update, update_data)

    assert dict_to_update == {
        "test1": "data1",
        "array": ["overwritten"],
        "dict": {
            "test4": "data4",
            "test5": "overwritten",
            "nested_dict": {
                "test6": "data6",
                "nested_array": [],
            },
            "test7": "added",
        },
        "test8": "added",
    }


def test__deep_update__creates_copy_of_updated_data() -> None:
    dict_to_update: dict = {}
    update_data: dict[str, Any] = {"array": [], "dict": {"nested_dict": {}}}

    deep_update(dict_to_update, update_data)
    update_data["array"].append("post_update_data")
    update_data["dict"]["nested_dict"]["new_key"] = "post_update_data"

    assert dict_to_update == {"array": [], "dict": {"nested_dict": {}}}


def test__deep_update__overwrite_strings() -> None:
    dict_to_update: dict = {
        "allow": {
            "user": {
                "create": {"allow": {"status": "NEW"}},
                "list": {"allow": "*"},
            },
        },
        "deny": {},
    }
    update_data = {
        "allow": {
            "user": {
                "create": {"allow": {"status": "OLD"}},
                "list": {
                    "allow": {"type": "ADMIN"},
                },
            },
        },
    }

    deep_update(dict_to_update, update_data)

    assert dict_to_update == {
        "allow": {
            "user": {
                "create": {"allow": {"status": "OLD"}},
                "list": {"allow": {"type": "ADMIN"}},
            },
        },
        "deny": {},
    }


def test__deprecated__logs_warning_for_function() -> None:
    expected_warning = r"smth - dont use me \(will be removed in 9.9.9\)."

    @deprecated(message="dont use me", version="9.9.9")
    def smth() -> None:
        pass

    with pytest.deprecated_call(match=expected_warning):
        smth()


def test__deprecated__logs_warning_for_method() -> None:
    expected_warning = r"smth - NOPE \(will be removed in 9.9.7\)."

    class SMTH:
        @deprecated(message="NOPE", version="9.9.7")
        def smth(self) -> None:
            pass

    with pytest.deprecated_call(match=expected_warning):
        SMTH().smth()
