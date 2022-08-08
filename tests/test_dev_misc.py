# coding=utf-8
from hashlib import sha1

from lbz.dev.misc import EVENT_TEMPLATE


def hash_string(string: str) -> str:
    return sha1(string.encode("UTF-8")).hexdigest()


def test_event() -> None:
    assert hash_string(EVENT_TEMPLATE) == "fe0ffbaaf59a43ccf384a99076675b1fcefcd9b2"
