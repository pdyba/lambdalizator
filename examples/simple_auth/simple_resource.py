from lbz.router import add_route
from lbz.response import Response
from lbz.resource import Resource
from lbz.authz import add_authz, authorize, set_authz


@set_authz
class HelloWorld(Resource):
    _name = "helloworld"

    @authorize
    @add_authz()
    @add_route("/", method="GET")
    def list(self, restrictions=None):
        return Response({"message": f"Hello, {self.request.user.username} !"})
