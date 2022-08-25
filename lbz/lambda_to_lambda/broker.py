from copy import deepcopy
from typing import Callable, Dict

from lbz.api_base import APIBase
from lbz.misc import get_logger

logger = get_logger(__name__)


class LambdaBroker(APIBase):
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
        self.op = raw_data[op_key]
        self.data = raw_data[data_key]
        self.context = context

    def handle(self) -> None:
        handler = self._get_handler()
        try:
            handler(deepcopy(self.data))
        except Exception:  # pylint: disable=broad-except
            logger.exception("Handling event failed, event: %s", self.op)

    def _get_handler(self) -> Callable:
        try:
            return self.mapper[self.op]
        except KeyError as err:
            raise NotImplementedError(f"No handlers implemented for {self.op}") from err
