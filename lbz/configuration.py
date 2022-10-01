from abc import ABCMeta, abstractmethod
from os import getenv
from typing import Any, Callable, Generic, Optional, TypeVar

from lbz.aws_ssm import SSM
from lbz.exceptions import ConfigurationError

T = TypeVar("T")


class ConfigValue(Generic[T], metaclass=ABCMeta):
    """Mandatory Configuration

    This class is not supporting None as outcome value.
    """
    def __init__(
        self,
        key: str,
        parser: Callable[[str], T] = str,  # type: ignore
        default: T = None,
    ):
        self._key = key
        self._parser = parser
        self._default = default
        self._value: T

    @abstractmethod
    def getter(self) -> Any:
        pass

    @property
    def value(self) -> T:
        if not hasattr(self, "_value"):
            val = self.getter()
            if val is not None:
                try:
                    self._value = self._parser(val)
                except Exception as error:
                    message = f"{self._key} could not be parsed with {self._parser}"
                    raise ConfigurationError(message) from error
            elif self._default is not None:
                self._value = self._default
            else:
                raise ConfigurationError(f"{self._key} was not defined.")

        return self._value


class EnvValue(ConfigValue):
    def getter(self) -> Optional[str]:
        return getenv(self._key)


class SSMValue(ConfigValue):
    def getter(self) -> Optional[str]:
        return SSM.get_parameter(self._key)
