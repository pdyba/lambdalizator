#!/usr/local/bin/python3.8
# coding=utf-8
from lbz.authz import Authorizer
from lbz.authz import add_authz


def test_add_authz_named():
    @add_authz(permission_name="x")
    def y():
        pass

    authz = Authorizer()
    assert authz["y"] == "x"


def test_add_authz_unnamed():
    @add_authz()
    def z():
        pass

    authz = Authorizer()
    assert authz["z"] == "z"
