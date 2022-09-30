from abc import abstractmethod
from os import getenv
from typing import Any, Callable, Optional

from lbz.aws_boto3 import SSM


class BaseConfig:
    def __init__(
        self,
        key: str,
        parser: Optional[Callable] = None,
        default: Optional[Any] = None,
    ):
        self.key = key
        self.parser = parser
        self.default = default
        self._value = None

    @abstractmethod
    def getter(self) -> Any:
        pass

    def get_value(self) -> Any:
        if self._value is None:
            val = self.getter()
            val = val if val is not None else self.default
            if val is None:
                self._value = None
            else:
                self._value = self.parser(val) if self.parser else val
        return self._value

    @property
    def value(self) -> Any:
        return self.get_value()


class KeyValue(BaseConfig):
    def __init__(
        self,
        value: Any,
    ):
        super().__init__("key", parser=None, default=None)
        self._value = value

    def getter(self) -> Any:
        return self._value


class EnvValue(BaseConfig):
    def getter(self) -> Any:
        return getenv(self.key)


class SSMValue(BaseConfig):
    def getter(self) -> Any:
        return SSM.get_parameter(self.key)
