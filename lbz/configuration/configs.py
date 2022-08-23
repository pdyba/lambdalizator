import json
from abc import abstractmethod
from os import getenv
from typing import Any, Callable, Optional

from lbz.configuration.aws_ssm import SSM


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


class KeyValueConfig(BaseConfig):
    def __init__(
        self,
        key: str,
        value: Any,
        parser: Optional[Callable] = None,
        default: Optional[Any] = None,
    ):
        super().__init__(key, parser=parser, default=default)
        self._value = value

    def getter(self) -> Any:
        return self._value


class EnvConfig(BaseConfig):
    def __init__(
        self,
        key: str,
        env_key: Optional[str] = None,
        parser: Any = str,
        default: Optional[Any] = None,
    ):
        super().__init__(key, parser=parser, default=default)
        self.env_key = env_key

    def getter(self) -> Any:
        return getenv(self.env_key or self.key)


class SSMConfig(BaseConfig):
    def __init__(self, key: str, ssm_key: str, parser: Any = str, default: Optional[Any] = None):
        super().__init__(key, parser=parser, default=default)
        self.ssm_key = ssm_key

    def getter(self) -> Any:
        return SSM.get_parameter(self.ssm_key)


class JSONFileConfig(BaseConfig):
    def __init__(
        self,
        key: str,
        json_file: str,
        json_key: Optional[str] = None,
        parser: Any = str,
        default: Optional[Any] = None,
    ):
        super().__init__(key, parser=parser, default=default)
        self.json_file = json_file
        self.json_key = json_key

    def getter(self) -> Any:
        with open(self.json_file, encoding="UTF-8") as file:
            return json.load(file).get(self.json_key or self.key)
