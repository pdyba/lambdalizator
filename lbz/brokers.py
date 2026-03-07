from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from lbz.misc import get_logger
from lbz.type_defs import LambdaContext

logger = get_logger(__name__)

T = TypeVar("T")


class BaseBroker(Generic[T], metaclass=ABCMeta):
    def __init__(self, event: dict, context: LambdaContext) -> None:
        self.raw_event = event
        self.context = context
        self.response: T | None = None

    def react(self) -> T:
        self.pre_handle()
        self.response = self.handle()

        # Post-handle should not affect the response, so exceptions are logged but not raised
        try:
            self.post_handle()
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(err)

        return self.response

    @abstractmethod
    def handle(self) -> T:
        pass

    @abstractmethod
    def pre_handle(self) -> None:
        pass

    @abstractmethod
    def post_handle(self) -> None:
        pass
