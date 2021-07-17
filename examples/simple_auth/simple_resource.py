# coding=utf-8
# pylint: disable=no-name-in-module, import-error, unused-argument
from lbz.router import add_route
from lbz.response import Response
from lbz.resource import Resource
from lbz.authz import authorization


class HelloWorldWithAuthorization(Resource):
    _name = "helloworld"

    @authorization
    @add_route("/", method="GET")
    def list(self, restrictions=None):
        return Response({"message": f"Hello, {self.request.user.username} !"})
