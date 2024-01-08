from collections.abc import Callable
from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Any

from lbz._cfg import AWS_LAMBDA_FUNCTION_NAME, EVENTS_BUS_NAME
from lbz.aws_boto3 import client
from lbz.events.event import Event
from lbz.misc import Singleton, get_logger

if TYPE_CHECKING:
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef
else:
    PutEventsRequestEntryTypeDef = dict

logger = get_logger(__name__)

# https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html
MAX_EVENTS_TO_SEND_AT_ONCE = 10


class EventAPI(metaclass=Singleton):
    def __init__(self) -> None:
        self._source = AWS_LAMBDA_FUNCTION_NAME.value
        self._resources: list[str] = []
        self._pending_events: list[Event] = []
        self._sent_events: list[Event] = []
        self._failed_events: list[Event] = []
        self._bus_name = EVENTS_BUS_NAME.value

    def __repr__(self) -> str:
        return (
            f"<EventAPI bus: {self._bus_name} Events: pending={len(self._pending_events)} "
            f"sent={len(self._sent_events)} failed={len(self._failed_events)}>"
        )

    def set_source(self, source: str) -> None:
        self._source = source

    def set_resources(self, resources: list[str]) -> None:
        self._resources = resources

    def set_bus_name(self, bus_name: str) -> None:
        self._bus_name = bus_name

    @property
    def bus_name(self) -> str:
        return self._bus_name

    @property
    def sent_events(self) -> list[Event]:
        return deepcopy(self._sent_events)

    @property
    def pending_events(self) -> list[Event]:
        return deepcopy(self._pending_events)

    @property
    def failed_events(self) -> list[Event]:
        return deepcopy(self._failed_events)

    def register(self, new_event: Event) -> None:
        self._pending_events.append(new_event)

    def send(self) -> None:
        success = True
        while self._pending_events:
            events = self._pending_events[:MAX_EVENTS_TO_SEND_AT_ONCE]
            try:
                entries = [self._create_eb_entry(event) for event in events]
                client.eventbridge.put_events(Entries=entries)
                self._sent_events.extend(events)
            except Exception as err:  # pylint: disable=broad-except
                self._failed_events.extend(events)
                logger.exception(err)
                success = False

            self._pending_events = self._pending_events[MAX_EVENTS_TO_SEND_AT_ONCE:]

        if not success:
            raise RuntimeError("Sending events has failed. Check logs for more details!")

    def clear(self) -> None:
        self.clear_sent()
        self.clear_pending()
        self.clear_failed()

    def clear_sent(self) -> None:
        self._sent_events = []

    def clear_pending(self) -> None:
        self._pending_events = []

    def clear_failed(self) -> None:
        self._failed_events = []

    def _create_eb_entry(self, new_event: Event) -> PutEventsRequestEntryTypeDef:
        return {
            "Detail": new_event.serialized_data,
            "DetailType": new_event.type,
            "EventBusName": self._bus_name,
            "Resources": self._resources,
            "Source": self._source,
        }


def event_emitter(function: Callable) -> Callable:
    """Decorator that makes function an emitter - automatically sends pending events on success"""
    EventAPI().clear()

    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            result = function(*args, **kwargs)
            EventAPI().send()
            return result
        except Exception as error:
            EventAPI().clear_pending()
            raise error

    return wrapped
