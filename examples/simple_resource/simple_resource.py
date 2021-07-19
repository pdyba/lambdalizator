# coding=utf-8
# pylint: disable=no-name-in-module, import-error
from lbz.router import add_route
from lbz.response import Response
from lbz.resource import Resource


class HelloWorld(Resource):
    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})
