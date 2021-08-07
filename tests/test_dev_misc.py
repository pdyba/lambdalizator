# coding=utf-8
from hashlib import sha1

from lbz.dev.misc import EVENT_TEMPLATE, Event


def hash_string(string):
    return sha1(string.encode("UTF-8")).hexdigest()


def test_event_base():
    assert hash_string(EVENT_TEMPLATE) == "fe0ffbaaf59a43ccf384a99076675b1fcefcd9b2"


def test_event():
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


def test_eq_():
    e1 = Event(
        resource_path="/",
        method="GET",
        body=None,
        query_params={"a": ["1", "2"], "b": ["3"]},
        path_params=None,
        headers=None,
    )
    e2 = Event(
        resource_path="/",
        method="GET",
        body=None,
        query_params={"a": ["1", "2"], "b": ["3"]},
        path_params=None,
        headers=None,
    )
    assert e1 == e2
