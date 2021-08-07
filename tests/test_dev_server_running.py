# coding=utf-8
from multiprocessing import Process
from time import sleep

import pytest
import requests

from lbz.dev.server import MyDevServer
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route


class ServerTester(Resource):
    @add_route("/method-test", method="GET")
    @add_route("/method-test", method="POST")
    @add_route("/method-test", method="OPTIONS")
    @add_route("/method-test", method="DELETE")
    @add_route("/method-test", method="PATCH")
    @add_route("/method-test", method="PUT")
    def method_tester(self):
        return Response({"m": self.method})

    @add_route("/query", method="GET")
    def query_tester(self):
        return Response({"q": str(self.request.query_params)})

    @add_route("/{id_1}/{id_2}", method="GET")
    def url_params_tester(self, id_1, id_2):
        return Response({"p": self.path_params})


def run(server, cls):
    server(cls).run()


class TestServerRunning:
    def setup_class(self):
        self.p = Process(target=run, args=(MyDevServer, ServerTester))
        self.p.daemon = True
        self.p.start()
        sleep(0.4)
        self.url = "http://localhost:8000"

    @pytest.mark.parametrize("method", ["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"])
    def test_methods(self, method):
        resp = requests.request(method, f"{self.url}/method-test").json()
        assert resp == {"m": method}

    def test_query_params(self):
        resp = requests.get(f"{self.url}/query?q=1&a=2&a=3").json()
        assert resp == {"q": "MultiDict({'q': ['1'], 'a': ['2', '3']})"}

    def test_url_params(self):
        resp = requests.get(f"{self.url}/a/b").json()
        assert resp == {"p": {"id_1": "a", "id_2": "b"}}
