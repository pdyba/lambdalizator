from lbz.events.event import Event
from lbz.exceptions import LambdaFWException
from lbz.resource import EventAwareResource
from lbz.response import Response
from lbz.router import add_route
from lbz.type_defs import LambdaContext


class SomeEvent(Event):
    type = "SOME_TYPE"


class HelloWorldExample(EventAwareResource):
    @add_route("/", method="GET")
    def list(self) -> Response:
        self.event_api.register(SomeEvent({"message": 24}))
        return Response({"message": "HelloWorld"})


def handle(event: dict, context: LambdaContext) -> dict:
    try:
        return HelloWorldExample(event)().to_dict()
    except Exception:  # pylint: disable=broad-except
        return LambdaFWException().get_response(context.aws_request_id).to_dict()
