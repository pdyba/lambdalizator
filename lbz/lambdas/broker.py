from typing import Callable, Dict, Union

from lbz.handlers import BaseHandler
from lbz.lambdas.enums import LambdaResult
from lbz.lambdas.response import LambdaResponse, lambda_error_response
from lbz.misc import get_logger

logger = get_logger(__name__)


class LambdaBroker(BaseHandler):
    def __init__(
        self,
        mapper: Dict[str, Callable[..., LambdaResponse]],
        event: dict,
        context: object = None,
    ) -> None:
        self.event = event
        self.context = context
        self.mapper = mapper
        self.data = event.get("data")

    def handle(self) -> LambdaResponse:
        handler = self._get_handler()
        if isinstance(handler, dict):
            return handler
        if self.data:
            response = handler(self.data)
        else:
            response = handler()
        return response

    def _get_handler(self) -> Union[Callable[..., LambdaResponse], LambdaResponse]:
        if (op := self.event.get("op")) is None:
            return lambda_error_response(
                result=LambdaResult.BAD_REQUEST,
                error_message="Lambda execution error: Missing 'op' field in the event.",
            )
        try:
            return self.mapper[op]
        except KeyError as error:
            raise NotImplementedError(f"{op} was no implemented") from error
