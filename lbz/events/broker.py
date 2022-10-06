from copy import deepcopy
from typing import Callable, Dict, List

from lbz.events.event import Event
from lbz.handlers import BaseHandler
from lbz.misc import get_logger

logger = get_logger(__name__)


# TODO: type_key and data_key will be const for EventBridge and different set for Cognito Events
class EventBroker(BaseHandler):
    def __init__(
        self,
        mapper: Dict[str, List[Callable[[Event], None]]],
        event: dict,
        context: object = None,
        *,
        type_key: str = "detail-type",
        data_key: str = "detail",
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

    def _get_handlers(self) -> List[Callable]:
        try:
            return self.mapper[self.event.type]
        except KeyError as err:
            raise NotImplementedError(f"No handlers implemented for {self.event.type}") from err

    def pre_handle(self) -> None:
        pass

    def post_handle(self) -> None:
        pass
