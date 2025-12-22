from typing import Protocol

from lbz.lambdas.response import LambdaResponse


class LambdaAPIFunction(Protocol):
    __name__: str

    def __call__(self, data: dict) -> LambdaResponse: ...
