from dataclasses import dataclass
from typing import Callable, Dict, List

from lbz.misc import get_logger

logger = get_logger(__name__)


@dataclass()
class Event:
    type: str
    data: dict


class EventBroker:
    def __init__(self, mapper: Dict[str, List[Callable]], raw_event: dict) -> None:
        self.mapper = mapper
        self.event = Event(type=raw_event["detail-type"], data=raw_event["detail"])

    def handle(self) -> None:
        self.pre_handle()

        for handler in self._get_handlers():
            try:
                handler(self.event)
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
