from typing import Callable, Dict

from lbz.exceptions import LambdaFWException
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

    def handle(self) -> LambdaResponse:
        if not (op := self.event.get("op")):
            return lambda_error_response(
                result=LambdaResult.BAD_REQUEST,
                error_message="Missing 'op' field in the event.",
            )
        try:
            handler = self._get_handler(op)
            if data := self.event.get("data"):
                response = handler(data)
            else:
                response = handler()
        except LambdaFWException as err:
            logger.exception('Unexpected error during "%s" operation!', op)
            return lambda_error_response(LambdaResult.SERVER_ERROR, err.message, err.error_code)
        except Exception as err:  # pylint: disable=broad-except
            logger.exception('Unexpected error during "%s" operation!', op)
            return lambda_error_response(LambdaResult.SERVER_ERROR, repr(err))

        return response

    def _get_handler(self, op: str) -> Callable[..., LambdaResponse]:
        try:
            return self.mapper[op]
        except KeyError as error:
            raise NotImplementedError(f"{op} was no implemented") from error
