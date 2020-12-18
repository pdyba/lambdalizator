#!/usr/local/bin/python3.8
# coding=utf-8
from hashlib import sha1

from lbz.dev.misc import event


def hash_string(string):
    return sha1(string.encode("UTF-8")).hexdigest()


def test_Event():
    pass


def test_event():
    assert hash_string(event) == "fe0ffbaaf59a43ccf384a99076675b1fcefcd9b2"
