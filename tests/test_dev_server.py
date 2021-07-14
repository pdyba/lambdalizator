#!/usr/local/bin/python3.8
# coding=utf-8
# pylint: disable=no-self-use, protected-access, too-few-public-methods
import io
import socket
from socketserver import BaseServer
from unittest import mock

from lbz.response import Response
from lbz.resource import Resource
from lbz.router import add_route

from lbz.dev.server import MyDevServer
from lbz.dev.server import MyLambdaDevHandler


class HelloWorld(Resource):
    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})

    @add_route("/t/{id}", method="GET")
    def get(self):
        return Response({"message": "HelloWorld"})


class MyLambdaDevHandlerHelloWorld(MyLambdaDevHandler):
    cls = HelloWorld


class MyClass:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect("0.0.0.0", "8888")


def test_my_lambda_dev_handler():
    with mock.patch("socket.socket") as msocket:
        msocket.makefile = lambda a, b: io.BytesIO(b"GET / HTTP/1.1\r\n")
        msocket.rfile.close = lambda: 0
        my_class = MyClass()
        handler = MyLambdaDevHandlerHelloWorld(msocket, ("127.0.0.1", 8888), BaseServer)
        my_class.tcp_socket.connect.assert_called_with("0.0.0.0", "8888")  # pylint: disable=no-member
    path, params = handler._get_route_params("/")
    assert path == "/"
    assert params is None

    path, params = handler._get_route_params("/t/123")
    assert path == "/t/{id}"
    assert params == {"id": "123"}


def test_my_dev_server():
    dev_serv = MyDevServer()
    assert dev_serv.server_address == ('localhost', 8000)
    assert dev_serv.port == 8000
    assert dev_serv.address == "localhost"
    assert issubclass(dev_serv.my_handler, MyLambdaDevHandler)
