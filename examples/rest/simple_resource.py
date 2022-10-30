#!/usr/bin/env python3.8
# coding=utf-8
"""
Simple Lambda Handler
"""
from lbz.dev.server import MyDevServer
from lbz.dev.test import Client
from lbz.exceptions import LambdaFWException
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route
from lbz.types import LambdaContext


class HelloWorldExample(Resource):
    @add_route("/", method="GET")
    def list(self) -> Response:
        return Response({"message": "HelloWorld"})


def handle(event: dict, context: LambdaContext) -> dict:
    try:
        exp = HelloWorldExample(event)
        resp = exp().to_dict()
        return resp
    except Exception:  # pylint: disable=broad-except
        return LambdaFWException().get_response(context.aws_request_id).to_dict()


class TestHelloWorld:
    def setup_method(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.client = Client(resource=HelloWorldExample)

    def test_filter_queries_all_active_when_no_params(self) -> None:
        data = self.client.get("/").to_dict()["body"]
        assert data == '{"message":"HelloWorld"}'


if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorldExample, port=8001)
    server.run()
