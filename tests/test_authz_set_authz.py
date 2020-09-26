#!/usr/local/bin/python3.8
# coding=utf-8
from lbz.authz import Authorizer
from lbz.authz import set_authz


class Base:
    _name = None
    _authorizer = Authorizer()


def test_set_authz():
    @set_authz
    class A(Base):
        _name = "b"

    a = A()
    assert a._authorizer.resource == "b"
