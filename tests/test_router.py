# coding=utf-8
import json

from lbz.misc import NestedDict
from lbz.router import Router, add_route


class TestRouter:
    def setup_method(self) -> None:
        # pylint: disable= attribute-defined-outside-init
        self.router = Router()
        self.router.add_route("/", "GET", "x")

    def teardown_method(self, _test_method) -> None:
        # pylint: disable= attribute-defined-outside-init
        self.router._del()  # pylint: disable=protected-access

    def test___init__(self) -> None:
        assert isinstance(self.router._routes, NestedDict)  # pylint: disable=protected-access

    def test___getitem__(self) -> None:
        assert self.router["/"] == {"GET": "x"}
        assert self.router["/"]["GET"] == "x"

    def test___str__(self) -> None:
        assert str(self.router) == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___repr__(self) -> None:
        assert repr(self.router) == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___contains__(self) -> None:
        assert "/" in self.router

    def test___len__(self) -> None:
        assert len(self.router) == 1

    def test___iter__(self) -> None:
        acc = 0
        for _ in self.router:
            acc += 1
        assert acc == 1

    def test_add_route(self) -> None:
        assert self.router["/"]["GET"] == "x"
        self.router.add_route("/", "POST", "x")
        assert self.router["/"]["POST"] == "x"
        self.router.add_route("/<uid>", "GET", "x")
        assert self.router["/<uid>"]["GET"] == "x"
        self.router.add_route("/x/y", "GET", "x")
        assert self.router["/x/y"]["GET"] == "x"


class TestAddRoute:
    def test_add_route(self) -> None:
        router = Router()
        assert len(router) == 0  # pylint: disable=compare-to-zero

        @add_route("/")
        def random_method() -> None:
            pass

        assert len(router) == 1
        assert router["/"] == {"GET": "random_method"}
        assert router["/"]["GET"] == "random_method"

        router._del()  # pylint: disable=protected-access
