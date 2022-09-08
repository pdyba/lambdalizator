from typing import Callable, Dict

from lbz.handler_base import HandlerBase
from lbz.misc import get_logger

logger = get_logger(__name__)


class LambdaBroker(HandlerBase):
    def __init__(
        self,
        mapper: Dict[str, Callable],
        raw_data: dict,
        *,
        op_key: str = "op",
        data_key: str = "data",
        context: object = None,
    ) -> None:
        self.mapper = mapper
        self.op = raw_data.get(op_key)
        self.data = raw_data.get(data_key)
        self.context = context

    def handle(self) -> dict:
        try:
            handler = self._get_handler()
            if self.data:
                response: dict = handler(self.data)
            else:
                response = handler()
            return response
        except Exception as err:  # pylint: disable=broad-except
            logger.exception("Handling event failed, operation: %s", self.op)
            return {"error": f"Lambda execution error: {repr(err)}"}

    def _get_handler(self) -> Callable:
        if self.op is None:
            raise TypeError('Missing "op" field in the event.')
        try:
            return self.mapper[self.op]
        except KeyError as err:
            raise NotImplementedError(f"No handler implemented for operation: {self.op}") from err
