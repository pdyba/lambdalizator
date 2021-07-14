# coding=utf-8
# pylint: disable=unused-argument,no-self-use, no-name-in-module, import-error
"""
Simple Dev Server
"""
from lbz.dev.server import MyDevServer

from simple_resource import HelloWorld

if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorld, port=8001)
    server.run()
