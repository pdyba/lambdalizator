from abc import abstractmethod
from os import getenv
from typing import Any, Callable, Generic, Optional, TypeVar

from lbz.aws_boto3 import SSM

T = TypeVar("T")


class BaseValue(Generic[T]):
    def __init__(
        self,
        key: str,
        parser: Optional[Callable[[str], T]] = None,
        default: T = None,
    ):
        self._key = key
        self._parser = parser
        self._default = default
        self._value: T

    @abstractmethod
    def getter(self) -> Optional[T]:
        pass

    @property
    def value(self) -> T:
        if not hasattr(self, "_value"):
            val = self.getter()
            val = val if val is not None else self.default
            if val is None:
                self._value = None  # type:ignore
            else:
                self._value = self.parser(val) if self.parser else val
        return self._value


class EnvValue(ConfigValue):
    def getter(self) -> Optional[str]:
        return getenv(self.key)


class SSMValue(ConfigValue):
    def getter(self) -> Optional[str]:
        return SSM.get_parameter(self.key)
