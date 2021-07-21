#!/usr/local/bin/python3.8
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


class HelloWorld(Resource):
    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})


def handle(event, context):
    try:
        exp = HelloWorld(event)
        resp = exp()
        return resp
    except Exception:  # pylint: disable=broad-except
        return LambdaFWException().get_response(context.aws_request_id).to_dict()


class PublicTestCase:
    def setup_method(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.client = Client(resource=HelloWorld)

    def test_filter_queries_all_active_when_no_params(self) -> None:
        data = self.client.get("/").to_dict()["body"]
        assert data == '{"message":"HelloWorld"}'


if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorld, port=8001)
    server.run()
