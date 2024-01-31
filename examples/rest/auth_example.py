"""Simple Lambda Handler with authorization"""
from lbz.authz.decorators import authorization
from lbz.dev.server import MyDevServer
from lbz.exceptions import ServerError
from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route
from lbz.type_defs import LambdaContext


class HelloWorldWithAuthorization(Resource):
    _name = "helloworld"

    @authorization()
    @add_route("/", method="GET")
    def list(self, restrictions: dict) -> Response:  # pylint: disable=unused-argument
        username = self.request.user.username if self.request.user else "no-name"
        return Response({"message": f"Hello, {username} !"})


def handle(event: dict, context: LambdaContext) -> dict:
    try:
        return HelloWorldWithAuthorization(event)().to_dict()
    except Exception:  # pylint: disable=broad-except
        return Response.from_exception(ServerError(), context.aws_request_id).to_dict()


if __name__ == "__main__":
    server = MyDevServer(acls=HelloWorldWithAuthorization, port=8001)
    server.run()
