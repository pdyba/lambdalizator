# coding=utf-8
from unittest.mock import patch

from lbz.dev.misc import Event
from lbz.dev.test import Client
from lbz.response import Response
from .test_dev_server import HelloWorld


class TestTestClient:
    def setup_class(self) -> None:
        self.client = Client(HelloWorld)  # pylint: disable=attribute-defined-outside-init

    def test_get(self) -> None:
        resp = self.client.get("/")
        assert isinstance(resp, Response)

    def test_post(self) -> None:
        resp = self.client.post("/")
        assert isinstance(resp, Response)

    def test_patch(self) -> None:
        resp = self.client.patch("/")
        assert isinstance(resp, Response)

    def test_put(self) -> None:
        resp = self.client.put("/")
        assert isinstance(resp, Response)

    def test_delete(self) -> None:
        resp = self.client.delete("/")
        assert isinstance(resp, Response)

    def test__process(self) -> None:
        with patch("uuid.uuid4", return_value="123"):
            with patch.object(self.client, "resource") as mocked_resource_new:
                # pylint: disable=protected-access
                self.client._process("/", "GET", None, {"a": [1, "2"], "b": 3}, None, None)
                mocked_resource_new.assert_called_once_with(
                    Event(
                        resource_path="/",
                        method="GET",
                        body=None,
                        query_params={"a": ["1", "2"], "b": ["3"]},
                        path_params=None,
                        headers=None,
                    )
                )
