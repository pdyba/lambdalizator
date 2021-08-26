# coding=utf-8
import io
import socket
from socketserver import BaseServer
from unittest.mock import patch, MagicMock, call

import pytest

from lbz.dev.server import MyDevServer, MyLambdaDevHandler
from tests.sample_test_resources import SimpleTestResource

# TODO: Check why in some tests there are two responses - its not affecting actual runtime


def test_my_dev_server_no_cls_raises():
    with pytest.raises(TypeError):
        MyLambdaDevHandler.cls()  # pylint: disable=no-value-for-parameter


class MyLambdaDevHandlerHelloWorld(MyLambdaDevHandler):
    cls = SimpleTestResource


class MockedHandler(MyLambdaDevHandler):
    cls = MagicMock


class MyClass:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect("0.0.0.0", "8888")


def test_my_lambda_dev_handler():
    with patch("socket.socket") as msocket:
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

    path, params = handler._get_route_params("/?=1&xx=2")  # pylint: disable=protected-access
    assert path == "/"
    assert params is None

    with pytest.raises(ValueError):
        handler._get_route_params("")  # pylint: disable=protected-access


@pytest.mark.parametrize(
    "method", ["do_GET", "do_PATCH", "do_POST", "do_PUT", "do_DELETE", "do_OPTIONS"]
)
def test_handle_request(method):
    with patch("socket.socket") as msocket:
        msocket.makefile = lambda a, b: io.BytesIO(b"GET / HTTP/1.1\r\n")
        msocket.rfile.close = lambda: 0
        handler = MockedHandler(msocket, ("127.0.0.1", 8888), BaseServer)
        with patch.object(handler, "handle_request") as mock_handler:
            getattr(handler, method)()
            mock_handler.assert_called_once()


def test_handle_favicon():
    with patch("socket.socket") as msocket:
        msocket.makefile = lambda a, b: io.BytesIO(b"GET /favicon.ico HTTP/1.1\r\n")
        msocket.rfile.close = lambda: 0
        handler = MyLambdaDevHandlerHelloWorld(msocket, ("127.0.0.1", 8888), BaseServer)
    assert handler.handle_request() is None


def test_handle_txt():
    with patch.object(MyLambdaDevHandler, "_send_json") as mocked_send:
        with patch("socket.socket") as msocket:
            msocket.makefile = lambda a, b: io.BytesIO(b"GET /txt HTTP/1.1\r\n")
            msocket.rfile.close = lambda: 0
            MyLambdaDevHandlerHelloWorld(msocket, ("127.0.0.1", 8888), BaseServer)

        mocked_send.assert_has_calls(
            [
                call(200, "HelloWorld", {"Content-Type": "text/plain"}),
                call(
                    500,
                    {"error": "Server error"},
                    headers={"Content-Type": "application/json;charset=UTF-8"},
                ),
            ]
        )


def test_handle_json():
    byte_string = (
        b'POST /p HTTP/1.1\r\nContent-Length: 8\r\nContent-Type: application/json\r\n\r\n{"a": 1}'
    )
    with patch.object(MyLambdaDevHandler, "_send_json") as mocked_send:
        with patch("socket.socket") as msocket:
            msocket.makefile = lambda a, b: io.BytesIO(byte_string)
            msocket.rfile.close = lambda: 0
            MyLambdaDevHandlerHelloWorld(msocket, ("127.0.0.1", 8888), BaseServer)

        mocked_send.assert_has_calls(
            [
                call(200, {"message": "uploaded"}, {"Content-Type": "application/json"}),
                call(
                    500,
                    {"error": "Server error"},
                    headers={"Content-Type": "application/json;charset=UTF-8"},
                ),
            ]
        )


def test_my_dev_server():
    dev_serv = MyDevServer(MyLambdaDevHandlerHelloWorld)
    assert dev_serv.server_address == ("localhost", 8000)
    assert dev_serv.port == 8000
    assert dev_serv.address == "localhost"
    assert issubclass(dev_serv.my_handler, MyLambdaDevHandler)


def test_my_dev_server_run():
    dev_serv = MyDevServer(MyLambdaDevHandlerHelloWorld)
    dev_serv.start()
    assert dev_serv.is_alive()
    dev_serv.stop()
    assert not dev_serv.is_alive()
