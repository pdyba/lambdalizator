#!/usr/local/bin/python3.8
# coding=utf-8
from lbz.dev.server import MyDevServer
from lbz.dev.server import MyLambdaDevHandler
from socketserver import BaseServer
from socket import socket

from unittest import mock
import socket
import io

from lbz.router import add_route
from lbz.response import Response
from lbz.resource import Resource


class HelloWorld(Resource):
    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})

    @add_route("/t/{id}", method="GET")
    def get(self):
        return Response({"message": "HelloWorld"})


class MyLambdaDevHandlerHelloWorld(MyLambdaDevHandler):
    cls = HelloWorld


class MyClass(object):
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect('0.0.0.0', '8888')


def test_MyLambdaDevHandler():
    with mock.patch('socket.socket') as msocket:
        msocket.makefile = lambda a, b: io.BytesIO(b'GET / HTTP/1.1\r\n')
        msocket.rfile.close = lambda: 0
        c = MyClass()
        handler = MyLambdaDevHandlerHelloWorld(msocket, ("127.0.0.1", 8888), BaseServer)
        c.tcp_socket.connect.assert_called_with('0.0.0.0', '8888')
    a, b = handler._get_route_params('/')
    assert a == "/"
    assert b == None

    a, b = handler._get_route_params('/t/123')
    assert a == "/t/{id}"
    assert b == {"id": "123"}


def test_MyDevServer():
    dev_serv = MyDevServer()
    # needs more testing.
