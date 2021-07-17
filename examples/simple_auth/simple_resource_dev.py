# coding=utf-8
# pylint: disable=no-self-use, no-name-in-module, import-error
"""
Simple Dev Server
"""
from lbz.dev.server import MyDevServer

from simple_resource import HelloWorldWithAuthorization

if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorldWithAuthorization, port=8001)
    server.run()
