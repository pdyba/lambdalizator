from lbz.resource import Resource
from lbz.response import Response
from lbz.router import add_route


class SimpleTestResource(Resource):
    @add_route("/", method="GET")
    def list(self) -> Response:
        return Response({"message": "HelloWorld"})

    @add_route("/txt", method="GET")
    def txt(self) -> Response:
        return Response("HelloWorld")

    @add_route("/p", method="POST")
    def upload(self) -> Response:
        return Response({"message": "uploaded"})

    @add_route("/t/{id}", method="GET")
    def get(self) -> Response:
        return Response({"message": "HelloWorld"})


class RunningServerTesterResource(Resource):
    @add_route("/method-test", method="GET")
    @add_route("/method-test", method="POST")
    @add_route("/method-test", method="OPTIONS")
    @add_route("/method-test", method="DELETE")
    @add_route("/method-test", method="PATCH")
    @add_route("/method-test", method="PUT")
    def method_tester(self) -> Response:
        return Response({"m": self.method})

    @add_route("/query", method="GET")
    def query_tester(self) -> Response:
        return Response({"q": str(self.request.query_params)})

    @add_route("/{id_1}/{id_2}", method="GET")
    def url_params_tester(self, id_1, id_2) -> Response:  # pylint: disable=unused-argument
        return Response({"p": self.path_params})
