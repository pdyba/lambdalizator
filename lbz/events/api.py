import json
from os import getenv
from typing import TYPE_CHECKING, List

from lbz.aws_boto3 import client
from lbz.misc import Singleton

if TYPE_CHECKING:
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef
else:
    PutEventsRequestEntryTypeDef = dict


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

    def register(self, new_event: BaseEvent) -> None:
        self._pending_events.append(new_event)

    def get_all_pending_events(self) -> List[BaseEvent]:
        return self._pending_events

    def get_all_sent_events(self) -> List[BaseEvent]:
        return self._sent_events

    def get_all_failed_events(self) -> List[BaseEvent]:
        return self._failed_events

    def send(self) -> None:
        try:
            if self._pending_events:
                entries = [self._create_eb_entry(event) for event in self._pending_events]
                client.eventbridge.put_events(Entries=entries)
            self._mark_sent()
        except Exception as err:
            self._mark_failed()
            raise err

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

    def _mark_sent(self) -> None:
        self._sent_events = self._pending_events
        self._pending_events = []
        self._failed_events = []

    def _mark_failed(self) -> None:
        self._failed_events = self._pending_events
        self._pending_events = []
        self._sent_events = []
