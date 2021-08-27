# coding=utf-8
from hashlib import sha1

import pytest

from lbz.dev.misc import EVENT_TEMPLATE, Event


def hash_string(string) -> None:
    return sha1(string.encode("UTF-8")).hexdigest()


def test_event_base() -> None:
    assert hash_string(EVENT_TEMPLATE) == "fe0ffbaaf59a43ccf384a99076675b1fcefcd9b2"


def test_event() -> None:
    event = Event(
        resource_path="/",
        method="GET",
        body={"test": 1},
        query_params={"q": "t"},
        path_params=None,
        headers={"header": "1"},
    )
    assert event["resource"] == "/"
    assert event["pathParameters"] == {}
    assert event["path"] == "/"
    assert event["method"] == "GET"
    assert event["body"] == {"test": 1}
    assert event["headers"] == {"header": "1"}
    assert event["queryStingParameters"] == {"q": "t"}
    assert event["multiValueQueryStringParameters"] == {"q": "t"}
    assert event["requestContext"]["resourcePath"] == "/"
    assert event["requestContext"]["path"] == "/"
    assert event["requestContext"]["httpMethod"] == "GET"
    assert isinstance(event["requestContext"]["requestId"], str)

    assert str(event) == "<Fake Event GET @ / body: {'test': 1}>"


def test_eq_() -> None:
    event_1 = Event(
        resource_path="/x",
        method="POST",
        body=None,
        query_params={"a": ["1", "2"], "b": ["3"]},
        path_params=None,
        headers=None,
    )
    event_2 = Event(
        resource_path="/x",
        method="POST",
        body=None,
        query_params={"a": ["1", "2"], "b": ["3"]},
        path_params=None,
        headers=None,
    )
    assert event_1 == event_2


def test_eq_raises() -> None:
    event_1 = Event(
        resource_path="/v",
        method="GET",
    )
    with pytest.raises(NotImplementedError):
        assert event_1 == "test"
