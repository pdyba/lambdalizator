# coding=utf-8
from lbz.dev.test import Client
from lbz.response import Response
from .test_dev_server import HelloWorld


def test_client():
    client = Client(HelloWorld)
    resp = client.get("/")
    assert isinstance(resp, Response)
