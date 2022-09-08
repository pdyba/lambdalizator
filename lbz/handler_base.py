from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from lbz.misc import deprecated

T = TypeVar("T")


class HandlerBase(Generic[T]):
    def react(self) -> T:
        self.pre_handle()
        response = self.handle()
        self.post_handle()
        return response

    @deprecated(message="Please use react() for full request flow")
    def __call__(self) -> T:
        return self.react()

    @abstractmethod
    def handle(self) -> T:
        pass

    def pre_handle(self) -> None:
        pass

    def post_handle(self) -> None:
        pass
