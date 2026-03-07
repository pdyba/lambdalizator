from typing import Protocol

from lbz.events.event import Event


class EventHandler(Protocol):
    __name__: str

    def __call__(self, event: Event) -> None: ...
