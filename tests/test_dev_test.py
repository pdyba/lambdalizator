#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access
from lbz.dev.test import Client
from lbz.response import Response
from .test_dev_server import HelloWorld


def test_client():
    client = Client(HelloWorld)
    resp = client.get("/")
    assert isinstance(resp, Response)
