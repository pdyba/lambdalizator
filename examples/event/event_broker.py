from collections.abc import Callable

from lbz.events import Event, EventBroker
from lbz.type_defs import LambdaContext


def my_event_handler(event: Event) -> None:
    print(f"TYPE: {event.type}")
    print(f"DATA: {event.data}")


event_to_handler_map: dict[str, list[Callable[[Event], None]]] = {"SOME_TYPE": [my_event_handler]}


def handle(event: dict, context: LambdaContext) -> None:
    EventBroker(mapper=event_to_handler_map, event=event, context=context).react()
