# coding=utf-8
import io
import json
import socket
from socketserver import BaseServer
from typing import Type
from unittest import mock
from urllib import request

from lbz.dev.server import MyDevServer, MyLambdaDevHandler
from lbz.resource import Resource


class MyClass:
    def __init__(self) -> None:
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect("0.0.0.0", "8888")


def test_my_lambda_dev_handler(sample_resource_without_authorization: Type[Resource]) -> None:
    with mock.patch("socket.socket") as msocket:

        class MyLambdaDevHandlerHelloWorld(MyLambdaDevHandler):
            cls = sample_resource_without_authorization

        msocket.makefile = lambda a, b: io.BytesIO(b"GET / HTTP/1.1\r\n")
        msocket.rfile.close = lambda: 0
        my_class = MyClass()
        handler = MyLambdaDevHandlerHelloWorld(msocket, ("127.0.0.1", 8888), BaseServer)
        my_class.tcp_socket.connect.assert_called_with(  # pylint: disable=no-member
            "0.0.0.0", "8888"
        )
    path, params = handler._get_route_params("/")  # pylint: disable=protected-access
    assert path == "/"
    assert params is None

    path, params = handler._get_route_params("/t/123")  # pylint: disable=protected-access
    assert path == "/t/{id}"
    assert params == {"id": "123"}


def test_my_dev_server(sample_resource_without_authorization: Type[Resource]) -> None:
    dev_serv = MyDevServer(sample_resource_without_authorization)
    assert dev_serv.server_address == ("localhost", 8000)
    assert dev_serv.port == 8000
    assert dev_serv.address == "localhost"
    assert issubclass(dev_serv.my_handler, MyLambdaDevHandler)


def test_server_can_run_in_background(
    sample_resource_without_authorization: Type[Resource],
) -> None:
    dev_serv = MyDevServer(sample_resource_without_authorization, port=9999)
    dev_serv.start()
    url = "http://localhost:9999/"

    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req) as response:
            assert response.status == 200
            assert json.loads(response.read().decode()) == {"message": "HelloWorld"}
    finally:
        dev_serv.stop()
