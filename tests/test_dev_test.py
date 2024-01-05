# coding=utf-8
from lbz.dev.test import Client
from lbz.resource import Resource
from lbz.response import Response


def test_client(sample_resource: type[Resource]) -> None:
    client = Client(sample_resource)
    resp = client.get("/")
    assert isinstance(resp, Response)
