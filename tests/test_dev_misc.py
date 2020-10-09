#!/usr/local/bin/python3.8
# coding=utf-8
from lbz.dev.misc import Event, admin, event
from hashlib import sha1


def hash_string(string):
    return sha1(string.encode("UTF-8")).hexdigest()


def test_Event():
    pass


def test_admin():
    assert hash_string(admin) == "447ab9d67869ac9db813b453e862bfb89e57f389"


def test_event():
    assert hash_string(event) == "fe0ffbaaf59a43ccf384a99076675b1fcefcd9b2"
