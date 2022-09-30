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
            logger.error('Missing "op" field in the processed event: %r', self.event)
            return lambda_error_response(LambdaResult.BAD_REQUEST, 'Missing "op" field in event.')
        if not (handler := self.mapper.get(op)):
            logger.error('No handler declared for requested operation: "%s"', op)
            return lambda_error_response(LambdaResult.BAD_REQUEST, f'"{op}" is not implemented.')

        try:
            if (data := self.event.get("data")) is not None:
                return handler(data)
            return handler()
        except LambdaFWException as err:
            logger.exception('Unexpected error in "%s" function!', handler.__name__)
            return lambda_error_response(LambdaResult.SERVER_ERROR, err.message, err.error_code)
        except Exception as err:  # pylint: disable=broad-except
            logger.exception('Unexpected error in "%s" function!', handler.__name__)
            return lambda_error_response(LambdaResult.SERVER_ERROR, repr(err))
