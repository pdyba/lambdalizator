#!/usr/local/bin/python3.8
# coding=utf-8
from lbz.dev.server import MyDevServer

from .simple_resource import HelloWorld

if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorld, port=8001)
    server.run()
