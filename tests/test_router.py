# coding=utf-8
import json

from lbz.misc import NestedDict
from lbz.router import Router, add_route


class TestRouter:
    def setup_method(self):
        # pylint: disable= attribute-defined-outside-init
        self.router = Router()
        self.router.add_route("/", "GET", "x")

    def teardown_method(self, _test_method):
        # pylint: disable= attribute-defined-outside-init
        self.router._del()  # pylint: disable=protected-access
        self.router = None

    def test___init__(self):
        assert isinstance(self.router._routes, NestedDict)  # pylint: disable=protected-access

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
        def random_method():
            pass

        assert len(router) == 1
        assert router["/"] == {"GET": "random_method"}
        assert router["/"]["GET"] == "random_method"
