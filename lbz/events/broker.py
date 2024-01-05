from collections.abc import Callable, Mapping
from copy import deepcopy

from lbz.events.event import Event
from lbz.handlers import BaseHandler
from lbz.misc import get_logger
from lbz.type_defs import LambdaContext

logger = get_logger(__name__)


class BaseEventBroker(BaseHandler[None]):
    def __init__(
        self,
        mapper: Mapping[str, list[Callable[[Event], None]]],
        event: dict,
        context: LambdaContext,
        *,
        type_key: str,
        data_key: str,
    ) -> None:
        super().__init__(event, context)
        self.mapper = mapper
        self.event = Event(event[data_key], event_type=event[type_key])

    def handle(self) -> None:
        self.pre_handle()

        for handler in self._get_handlers():
            try:
                handler(deepcopy(self.event))
            except Exception:  # pylint: disable=broad-except
                logger.exception("Handling event failed, event: %s", self.event)

        self.post_handle()

    def _get_handlers(self) -> list[Callable]:
        try:
            return self.mapper[self.event.type]
        except KeyError as err:
            raise NotImplementedError(f"No handlers implemented for {self.event.type}") from err


class EventBroker(BaseEventBroker):
    def __init__(
        self,
        mapper: Mapping[str, list[Callable[[Event], None]]],
        event: dict,
        context: LambdaContext,
    ) -> None:
        super().__init__(mapper, event, context, type_key="detail-type", data_key="detail")


class CognitoEventBroker(BaseEventBroker):
    def __init__(
        self,
        mapper: Mapping[str, list[Callable[[Event], None]]],
        event: dict,
        context: LambdaContext,
    ) -> None:
        super().__init__(mapper, event, context, type_key="triggerSource", data_key="request")
        self.event.data["userName"] = event["userName"]
