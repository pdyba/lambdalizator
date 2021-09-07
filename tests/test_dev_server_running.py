# coding=utf-8
import pytest
import requests

from lbz.dev.server import MyDevServer

from tests.sample_test_resources import RunningServerTesterResource


class TestServerRunning:
    def setup_class(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.proc = MyDevServer(acls=RunningServerTesterResource)
        self.proc.start()
        self.url = "http://localhost:8000"

    def teardown_class(self) -> None:
        self.proc.stop()

    @pytest.mark.parametrize("method", ["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"])
    def test_methods(self, method) -> None:
        resp = requests.request(method, f"{self.url}/method-test").json()
        assert resp == {"m": method}

    def test_query_params(self) -> None:
        resp = requests.get(f"{self.url}/query?q=1&a=2&a=3").json()
        assert resp == {"q": "MultiDict({'q': ['1'], 'a': ['2', '3']})"}

    def test_url_params(self) -> None:
        resp = requests.get(f"{self.url}/a/b").json()
        assert resp == {"p": {"id_1": "a", "id_2": "b"}}
