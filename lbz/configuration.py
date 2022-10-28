import json
from abc import ABCMeta, abstractmethod
from os import getenv
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from lbz.aws_ssm import SSM
from lbz.exceptions import ConfigValueParsingFailed, MissingConfigValue

T = TypeVar("T")


class ConfigParser:
    @staticmethod
    def split_by_comma(value: str) -> List[str]:
        return value.split(",")

    @staticmethod
    def cast_to_bool(value: str) -> bool:
        if value.lower() in ("true", "1"):
            return True
        return False

    @staticmethod
    def load_jwt_keys(value: str) -> List[dict]:
        deserialized_value: Dict[str, List[dict]] = json.loads(value)
        return deserialized_value["keys"]


class ConfigValue(Generic[T], metaclass=ABCMeta):
    """Mandatory Configuration

    This class is not supporting None as outcome value.
    """

    # TODO: There is space for improvement around default str argument
    def __init__(
        self,
        key: str,
        parser: Callable[[Any], T] = str,  # type: ignore
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
            if (val := self.getter()) is not None:
                self._value = self._parse_value(val)
            elif self._default is not None:
                self._value = self._default
            else:
                raise MissingConfigValue(self._key)

        return self._value

    def _parse_value(self, value: Any) -> T:
        try:
            return self._parser(value)
        except Exception as error:
            raise ConfigValueParsingFailed(self._key, value) from error

    def reset(self) -> None:
        self._value = None


class EnvValue(ConfigValue[T]):
    def getter(self) -> Optional[str]:
        return getenv(self._key)


class SSMValue(ConfigValue[T]):
    def getter(self) -> Optional[str]:
        return SSM.get_parameter(self._key)
