from typing import Optional

from examples.event.event_aware_resource import HelloWorldExample
from examples.event.event_broker import event_to_handler_map
from lbz.events import EventBroker
from lbz.exceptions import LambdaFWException
from lbz.lambdas import LambdaSource
from lbz.type_defs import LambdaContext


def handle(event: dict, context: LambdaContext) -> Optional[dict]:
    try:
        if LambdaSource.is_from(event, LambdaSource.API_GW):
            return HelloWorldExample(event)().to_dict()
        if LambdaSource.is_from(event, LambdaSource.EVENT_BRIDGE):
            EventBroker(mapper=event_to_handler_map, event=event, context=context).react()
        return None
    except Exception:  # pylint: disable=broad-except
        return LambdaFWException().get_response(context.aws_request_id).to_dict()
