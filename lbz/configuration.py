from abc import ABCMeta, abstractmethod
from os import getenv
from typing import Any, Callable, Generic, Optional, TypeVar

from lbz.aws_ssm import SSM
from lbz.exceptions import ConfigurationMissingError, ConfigurationParsingError

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
        self._value: Optional[T] = None

    @abstractmethod
    def getter(self) -> Any:
        pass

    @property
    def value(self) -> T:
        if self._value is None:
            val = self.getter()
            if val is not None:
                self._value = self._parse_value(val)
            elif self._default is not None:
                self._value = self._default
            else:
                raise ConfigurationMissingError(f"'{self._key}' was not defined.")

        return self._value

    def _parse_value(self, value: Any) -> T:
        try:
            return self._parser(value)
        except Exception as error:
            message = f"'{self._key}' could not be parsed with '{self._parser}'"
            raise ConfigurationParsingError(message) from error


class EnvValue(ConfigValue):
    def getter(self) -> Optional[str]:
        return getenv(self._key)


class SSMValue(ConfigValue):
    def getter(self) -> Optional[str]:
        return SSM.get_parameter(self._key)
