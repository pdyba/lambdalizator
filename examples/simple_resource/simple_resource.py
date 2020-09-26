from lbz.router import add_route
from lbz.communication import Response
from lbz.resource import Resource


class HelloWorld(Resource):
    @add_route("/", method="GET")
    def list(self):
        return Response({"message": "HelloWorld"})
