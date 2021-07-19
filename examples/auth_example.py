# coding=utf-8
# pylint: disable=no-name-in-module, import-error
from lbz.authz import authorization
from lbz.exceptions import ServerError
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route


class HelloWorldWithAuthorization(Resource):
    _name = "helloworld"

    @authorization
    @add_route("/", method="GET")
    def list(self, restrictions=None):  # pylint: disable=unused-argument
        return Response({"message": f"Hello, {self.request.user.username} !"})


def handle(event, context):
    try:
        return HelloWorldWithAuthorization(event)()
    except Exception:  # pylint: disable=broad-except
        return ServerError().get_response(context.aws_request_id)  # pylint: disable=no-member
