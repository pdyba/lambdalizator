#!/usr/local/bin/python3.8
# coding=utf-8
import pytest

from lbz.authz import Authorizer
from lbz.authz import authorize, add_authz
from lbz.exceptions import PermissionDenied


def test_wrapper():
    class A:
        _authorizer = Authorizer()

        @authorize
        @add_authz()
        def y(self, restrictions=None):
            return True

    authz = Authorizer()
    assert authz["y"] == "y"
    a = A()
    with pytest.raises(PermissionDenied):
        assert a.y()

    a._authorizer.allow = {"*": "*"}
    assert a.y()
