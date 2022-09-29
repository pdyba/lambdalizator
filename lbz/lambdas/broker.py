from typing import Callable, Dict, Optional, cast

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
        self.response: Optional[LambdaResponse] = None
        self.op: Optional[str] = None
        self.handler: Callable[..., LambdaResponse]
        self.validate_request()

    def handle(self) -> LambdaResponse:
        if self.response:
            return self.response
        try:
            if data := self.event.get("data"):
                response = self.handler(data)
            else:
                response = self.handler()
        except LambdaFWException as err:
            logger.exception('Unexpected error during "%s" operation!', self.op)
            return lambda_error_response(LambdaResult.SERVER_ERROR, err.message, err.error_code)
        except Exception as err:  # pylint: disable=broad-except
            logger.exception('Unexpected error during "%s" operation!', self.op)
            return lambda_error_response(LambdaResult.SERVER_ERROR, repr(err))

        return response

    def validate_request(self) -> None:
        self.op = cast(str, self.event.get("op"))
        if not self.op:
            self.response = lambda_error_response(
                result=LambdaResult.BAD_REQUEST,
                error_message="Missing 'op' field in the event.",
            )
        else:
            try:
                self.handler = self.mapper[self.op]
            except KeyError:
                msg = f"Handler for {self.op} was no implemented"
                logger.exception(msg)
                self.response = lambda_error_response(LambdaResult.BAD_REQUEST, msg)
