from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from lbz.misc import deprecated, get_logger
from lbz.type_defs import LambdaContext

logger = get_logger(__name__)

T = TypeVar("T")


class BaseHandler(Generic[T], metaclass=ABCMeta):
    def __init__(self, event: dict, context: LambdaContext) -> None:
        self.raw_event = event
        self.context = context
        self.response: T | None = None

    def react(self) -> T:
        self.pre_handle()
        self.response = self.handle()
        self._post_handle()
        return self.response

    @deprecated(message="Please use react() for full request flow", version="0.7.0")
    def __call__(self) -> T:
        return self.react()

    @abstractmethod
    def handle(self) -> T:
        pass

    def pre_handle(self) -> None:
        pass

    def post_handle(self) -> None:
        pass

    def _post_handle(self) -> None:
        """Makes the post_handle runtime friendly."""
        try:
            self.post_handle()
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(err)
