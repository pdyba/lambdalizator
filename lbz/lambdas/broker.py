from collections.abc import Callable, Mapping

from lbz.exceptions import LambdaFWException
from lbz.handlers import BaseHandler
from lbz.lambdas.enums import LambdaResult
from lbz.lambdas.response import LambdaResponse, lambda_error_response
from lbz.misc import get_logger
from lbz.type_defs import LambdaContext

logger = get_logger(__name__)


class LambdaBroker(BaseHandler[LambdaResponse]):
    def __init__(
        self,
        mapper: Mapping[str, Callable[[dict], LambdaResponse]],
        event: dict,
        context: LambdaContext,
    ) -> None:
        super().__init__(event, context)
        self.mapper = mapper

    def handle(self) -> LambdaResponse:
        if not (op := self.raw_event.get("op")):
            logger.error('Missing "op" field in the processed event: %r', self.raw_event)
            return lambda_error_response(LambdaResult.CONTRACT_ERROR, 'Missing "op" field.')
        if not (handler := self.mapper.get(op)):
            logger.error('No handler declared for requested operation: "%s"', op)
            return lambda_error_response(LambdaResult.CONTRACT_ERROR, f'"{op}" not implemented.')
        try:
            return handler(self.raw_event.get("data") or {})
        except LambdaFWException as err:
            logger.exception('Unexpected error in "%s" function!', handler.__name__)
            return lambda_error_response(LambdaResult.SERVER_ERROR, err.message, err.error_code)
        except Exception as err:  # pylint: disable=broad-except
            logger.exception('Unexpected error in "%s" function!', handler.__name__)
            return lambda_error_response(LambdaResult.SERVER_ERROR, repr(err))
