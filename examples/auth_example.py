#!/usr/bin/env python3.8
# coding=utf-8
"""
Simple Lambda Handler with authorization
"""
from lbz.authz import authorization
from lbz.dev.server import MyDevServer
from lbz.exceptions import ServerError
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route


class HelloWorldWithAuthorization(Resource):
    _name = "helloworld"

    @authorization()
    @add_route("/", method="GET")
    def list(self, restrictions=None):  # pylint: disable=unused-argument
        return Response({"message": f"Hello, {self.request.user.username} !"})


def handle(event, context):
    try:
        return HelloWorldWithAuthorization(event)()
    except Exception:  # pylint: disable=broad-except
        return ServerError().get_response(context.aws_request_id).to_dict()


if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorldWithAuthorization, port=8001)
    server.run()
