# coding=utf-8
import json

from lbz.misc import NestedDict
from lbz.router import Router, add_route


class TestRouter:
    def test___init__(self, sample_router: Router) -> None:
        assert isinstance(sample_router._routes, NestedDict)  # pylint: disable=protected-access

    def test___getitem__(self, sample_router: Router) -> None:
        assert sample_router["/"] == {"GET": "x"}
        assert sample_router["/"]["GET"] == "x"

    def test___str__(self, sample_router: Router) -> None:
        assert str(sample_router) == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___repr__(self, sample_router: Router) -> None:
        assert repr(sample_router) == json.dumps({"/": {"GET": "x"}}, indent=4)

    def test___contains__(self, sample_router: Router) -> None:
        assert "/" in sample_router

    def test___len__(self, sample_router: Router) -> None:
        assert len(sample_router) == 1

    def test___iter__(self, sample_router: Router) -> None:
        acc = 0
        for _ in sample_router:
            acc += 1
        assert acc == 1

    def test_add_route(self, sample_router: Router) -> None:
        assert sample_router["/"]["GET"] == "x"
        sample_router.add_route("/", "POST", "x")
        assert sample_router["/"]["POST"] == "x"
        sample_router.add_route("/<uid>", "GET", "x")
        assert sample_router["/<uid>"]["GET"] == "x"
        sample_router.add_route("/x/y", "GET", "x")
        assert sample_router["/x/y"]["GET"] == "x"


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
