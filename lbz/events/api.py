import json
from copy import deepcopy
from os import getenv
from typing import TYPE_CHECKING, List

from lbz.aws_boto3 import client
from lbz.misc import Singleton, get_logger

if TYPE_CHECKING:
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef
else:
    PutEventsRequestEntryTypeDef = dict

logger = get_logger(__name__)

# https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html
MAX_EVENTS_TO_SEND_AT_ONCE = 10


class BaseEvent:
    type: str

    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data
        self.data: str = self.serialize(raw_data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseEvent):
            return self.type == other.type and self.raw_data == other.raw_data
        return False

    @staticmethod
    def serialize(raw_data: dict) -> str:
        return json.dumps(raw_data, default=str)


class EventAPI(metaclass=Singleton):
    def __init__(self) -> None:
        self._source = getenv("AWS_LAMBDA_FUNCTION_NAME") or "lbz-event-api"
        self._resources: List[str] = []
        self._pending_events: List[BaseEvent] = []
        self._sent_events: List[BaseEvent] = []
        self._failed_events: List[BaseEvent] = []
        self._bus_name = getenv("EVENTS_BUS_NAME", f"{self._source}-event-bus")

    def __repr__(self) -> str:
        return (
            f"<EventAPI bus: {self._bus_name} Events: pending={len(self._pending_events)} "
            f"sent={len(self._sent_events)} failed={len(self._failed_events)}>"
        )

    def set_source(self, source: str) -> None:
        self._source = source

    def set_resources(self, resources: List[str]) -> None:
        self._resources = resources

    def set_bus_name(self, bus_name: str) -> None:
        self._bus_name = bus_name

    @property
    def sent_events(self) -> List[BaseEvent]:
        return deepcopy(self._sent_events)

    @property
    def pending_events(self) -> List[BaseEvent]:
        return deepcopy(self._pending_events)

    @property
    def failed_events(self) -> List[BaseEvent]:
        return deepcopy(self._failed_events)

    def register(self, new_event: BaseEvent) -> None:
        self._pending_events.append(new_event)

    # TODO: Stop sharing protected lists outside the class, use the above properties instead
    def get_all_pending_events(self) -> List[BaseEvent]:
        return self._pending_events

    def get_all_sent_events(self) -> List[BaseEvent]:
        return self._sent_events

    def get_all_failed_events(self) -> List[BaseEvent]:
        return self._failed_events

    def send(self) -> None:
        self._sent_events = []
        self._failed_events = []

        while self._pending_events:
            events = self._pending_events[:MAX_EVENTS_TO_SEND_AT_ONCE]
            try:
                entries = [self._create_eb_entry(event) for event in events]
                client.eventbridge.put_events(Entries=entries)
                self._sent_events.extend(events)
            except Exception as err:  # pylint: disable=broad-except
                self._failed_events.extend(events)
                logger.exception(err)

            self._pending_events = self._pending_events[MAX_EVENTS_TO_SEND_AT_ONCE:]

        if self._failed_events:
            raise RuntimeError("Sending events has failed. Check logs for more details!")

    def clear(self) -> None:
        self._sent_events = []
        self._pending_events = []
        self._failed_events = []

    def _create_eb_entry(self, new_event: BaseEvent) -> PutEventsRequestEntryTypeDef:
        return {
            "Detail": new_event.data,
            "DetailType": new_event.type,
            "EventBusName": self._bus_name,
            "Resources": self._resources,
            "Source": self._source,
        }
