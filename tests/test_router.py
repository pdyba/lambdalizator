#!/usr/local/bin/python3.8
# coding=utf-8
from lbz.router import add_route
from lbz.router import Router
from lbz.misc import NestedDict
import json


class TestRouter:
    def setup_method(self):
        self.r = Router()
        self.r.add_route("/", "GET", "x")

    def teardown_method(self, test_method):
        self.r._del()
        self.r = None

    def test___init__(self):
        assert isinstance(self.r._routes, NestedDict)

    def test___getitem__(self):
        assert self.r["/"] == {"GET": "x"}
        assert self.r["/"]["GET"] == "x"

    def test___str__(self):
        assert str(self.r) == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___repr__(self):
        assert self.r.__repr__() == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___contains__(self):
        assert "/" in self.r

    def test___len__(self):
        assert len(self.r) == 1

    def test___iter__(self):
        acc = 0
        for x in self.r:
            acc += 1
        assert acc == 1

    def test_add_route(self):
        assert self.r["/"]["GET"] == "x"
        self.r.add_route("/", "POST", "x")
        assert self.r["/"]["POST"] == "x"
        self.r.add_route("/<uid>", "GET", "x")
        assert self.r["/<uid>"]["GET"] == "x"
        self.r.add_route("/x/y", "GET", "x")
        assert self.r["/x/y"]["GET"] == "x"


class TestAddRoute:
    def test_add_route(self):
        router = Router()
        assert len(router) == 0

        @add_route("/")
        def x():
            pass

        assert len(router) == 1
        assert router["/"] == {"GET": "x"}
        assert router["/"]["GET"] == "x"
