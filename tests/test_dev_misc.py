#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access, too-few-public-methods
from hashlib import sha1

from lbz.dev.misc import EVENT


def hash_string(string):
    return sha1(string.encode("UTF-8")).hexdigest()


def test_event():
    assert hash_string(EVENT) == "fe0ffbaaf59a43ccf384a99076675b1fcefcd9b2"
