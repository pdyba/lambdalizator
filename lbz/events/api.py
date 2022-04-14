import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_events.type_defs import PutEventsRequestEntryTypeDef
else:
    PutEventsRequestEntryTypeDef = dict

from os import getenv
from typing import List

from lbz.boto3_client import clients
from lbz.misc import Singleton


class BaseEvent:
    type: str

    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data
        self.data: str = self.serialize(raw_data)

    @staticmethod
    def serialize(data: dict) -> str:
        return json.dumps(data, default=str)


class EventAPI(metaclass=Singleton):
    def __init__(self) -> None:
        self._source = getenv("AWS_LAMBDA_FUNCTION_NAME") or "lbz-event-api"
        self._resources: List[str] = []
        self.entries: List[PutEventsRequestEntryTypeDef] = []
        self.bus_name = getenv("EVENT_BRIDGE_BUS_NAME", f"{self._source}-event-bus")

    def set_source(self, source: str) -> None:
        self._source = source

    def set_resource(self, resources: List[str]) -> None:
        self._resources = resources

    def register(self, new_event: BaseEvent) -> None:
        self.entries.append(self.create_eb_entry(new_event))

    def get_all_registered_events(self) -> List[PutEventsRequestEntryTypeDef]:
        return self.entries

    def send(self) -> None:
        if self.entries:
            clients.eventbridge.put_events(Entries=self.entries)

    def create_eb_entry(self, new_event: BaseEvent) -> PutEventsRequestEntryTypeDef:
        return {
            "Detail": new_event.data,
            "DetailType": new_event.type,
            "EventBusName": self.bus_name,
            "Resources": self._resources,
            "Source": self._source,
        }
