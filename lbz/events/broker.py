from collections.abc import Mapping
from copy import deepcopy

from lbz.brokers import BaseBroker
from lbz.events.event import Event
from lbz.events.protocols import EventHandler
from lbz.misc import get_logger
from lbz.type_defs import LambdaContext

logger = get_logger(__name__)


class BaseEventBroker(BaseBroker[None]):
    def __init__(
        self,
        mapper: Mapping[str, list[EventHandler]],
        event: dict,
        context: LambdaContext,
        *,
        type_key: str,
        data_key: str,
    ) -> None:
        super().__init__(event, context)
        self.mapper = mapper
        self.event = Event(event[data_key], event_type=event[type_key])

    @property
    def handlers(self) -> list[EventHandler]:
        try:
            return self.mapper[self.event.type]
        except KeyError as error:
            raise NotImplementedError(f"No handlers implemented for {self.event.type}") from error

    def handle(self) -> None:
        for handler in self.handlers:
            try:
                handler(deepcopy(self.event))
            except Exception as error:  # pylint: disable=broad-except
                self.on_error(error)

    def on_error(self, error: Exception) -> None:  # pylint: disable=unused-argument
        logger.exception("Handling event failed, event: %s", self.event)

    def pre_handle(self) -> None:
        pass

    def post_handle(self) -> None:
        pass


class EventBroker(BaseEventBroker):
    def __init__(
        self,
        mapper: Mapping[str, list[EventHandler]],
        event: dict,
        context: LambdaContext,
    ) -> None:
        super().__init__(mapper, event, context, type_key="detail-type", data_key="detail")


class CognitoEventBroker(BaseEventBroker):
    def __init__(
        self,
        mapper: Mapping[str, list[EventHandler]],
        event: dict,
        context: LambdaContext,
    ) -> None:
        super().__init__(mapper, event, context, type_key="triggerSource", data_key="request")
        self.event.data["userName"] = event["userName"]
