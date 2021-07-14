#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access, too-few-public-methods
from lbz.router import add_route
from lbz.router import Router
from lbz.misc import NestedDict
import json


# pylint: disable= attribute-defined-outside-init
class TestRouter:
    def setup_method(self):
        self.router = Router()
        self.router.add_route("/", "GET", "x")

    def teardown_method(self, test_method):  # pylint: disable=unused-argument
        self.router._del()
        self.router = None

    def test___init__(self):
        assert isinstance(self.router._routes, NestedDict)

    def test___getitem__(self):
        assert self.router["/"] == {"GET": "x"}
        assert self.router["/"]["GET"] == "x"

    def test___str__(self):
        assert str(self.router) == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___repr__(self):
        assert self.router.__repr__() == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___contains__(self):
        assert "/" in self.router

    def test___len__(self):
        assert len(self.router) == 1

    def test___iter__(self):
        acc = 0
        for _ in self.router:
            acc += 1
        assert acc == 1

    def test_add_route(self):
        assert self.router["/"]["GET"] == "x"
        self.router.add_route("/", "POST", "x")
        assert self.router["/"]["POST"] == "x"
        self.router.add_route("/<uid>", "GET", "x")
        assert self.router["/<uid>"]["GET"] == "x"
        self.router.add_route("/x/y", "GET", "x")
        assert self.router["/x/y"]["GET"] == "x"


class TestAddRoute:
    def test_add_route(self):
        router = Router()
        assert len(router) == 0

        @add_route("/")
        def random_method():  # pylint: disable=unused-variable
            pass

        assert len(router) == 1
        assert router["/"] == {"GET": "random_method"}
        assert router["/"]["GET"] == "random_method"
