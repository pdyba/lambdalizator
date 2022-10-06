import json
import re
from os import environ
from unittest.mock import MagicMock, patch

import pytest

from lbz.aws_ssm import SSM
from lbz.configuration import ConfigValue, EnvValue, SSMValue
from lbz.exceptions import ConfigValueParsingFailed, MissingConfigValue


class TestConfigValue:
    # We are using EnvValue instead ConfigValue in order to not create artificial class
    # that wouldn't add any value.
    @patch.dict(environ, {"key": "42"}, clear=True)
    def test_if_getter_was_used_only_once(self) -> None:
        cfg = EnvValue("key")

        with patch.object(EnvValue, "getter", wraps=cfg.getter) as mocked_getter:
            assert cfg.value == "42"
            assert cfg.value == "42"

        mocked_getter.assert_called_once()

    def test_returns_default_when_no_value_set(self) -> None:
        cfg = EnvValue("test", default=42, parser=int)

        assert cfg.value == 42

    def test_raises_missing_configuration_when_value_is_none(self) -> None:
        cfg = EnvValue("test")

        with pytest.raises(MissingConfigValue, match="'test' was not defined."):
            cfg.value  # pylint: disable=pointless-statement

    def test_modifies_config_value_using_declared_parser_function(self) -> None:
        class MyIntConfigValue(ConfigValue):
            def getter(self) -> int:
                return 1

        cfg = MyIntConfigValue("key", lambda a: a * 10)

        assert cfg.value == 10

    def test_raises_if_parser_failed(self) -> None:
        class MyFailingConfigValue(ConfigValue):
            def getter(self) -> tuple:
                return 1, 2

        msg = re.escape("'key' could not parse '(1, 2)'")

        cfg = MyFailingConfigValue("key", parser=int)

        with pytest.raises(ConfigValueParsingFailed, match=msg):
            cfg.value  # pylint: disable=pointless-statement

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_int_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=int)

        assert env_cfg.value == 12

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_list_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=list)

        assert env_cfg.value == ["1", "2"]

    @patch.dict(environ, {"RANDOM_VAR": '{"test": "ttt"}'}, clear=True)
    def test_gets_value_from_env_with_json_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=json.loads)

        assert env_cfg.value == {"test": "ttt"}


class TestEnvConfig:
    @patch.dict(environ, {"RANDOM_VAR": "12.2.1"}, clear=True)
    def test_gets_value_from_env(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR")

        assert env_cfg.value == "12.2.1"


class TestSSMConfig:
    @patch.object(SSM, "get_parameter", autospec=True)
    def test_getter_calls_ssm_with_specific_key(self, mocked_get_parameter: MagicMock) -> None:
        mocked_get_parameter.return_value = "test_value"
        cfg = SSMValue("key_name")

        assert cfg.value == "test_value"

        mocked_get_parameter.assert_called_once_with("key_name")
