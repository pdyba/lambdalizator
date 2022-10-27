import json
import re
from os import environ
from unittest.mock import MagicMock, patch

import pytest

from lbz.aws_ssm import SSM
from lbz.configuration import ConfigParser, EnvValue, SSMValue
from lbz.exceptions import ConfigValueParsingFailed, MissingConfigValue


class TestConfigValue:
    # We are using EnvValue instead ConfigValue in order to not create artificial class
    # that wouldn't add any value.
    @patch.dict(environ, {"key": "42"})
    def test_if_getter_was_used_only_once(self) -> None:
        cfg = EnvValue[str]("key")

        with patch.object(EnvValue, "getter", wraps=cfg.getter) as mocked_getter:
            assert cfg.value == "42"
            assert cfg.value == "42"

        mocked_getter.assert_called_once()

    def test_returns_default_when_no_value_set(self) -> None:
        cfg = EnvValue("test", default=42, parser=int)

        assert cfg.value == 42

    def test_raises_missing_configuration_when_value_is_none(self) -> None:
        cfg = EnvValue[str]("test")

        with pytest.raises(MissingConfigValue, match="'test' was not defined."):
            cfg.value  # pylint: disable=pointless-statement

    @patch.object(EnvValue, "getter", MagicMock(return_value=1))
    def test_modifies_config_value_using_declared_parser_function(self) -> None:
        def times_10_parser(value: int) -> int:
            return value * 10

        cfg = EnvValue[int]("RANDOM_VAR", times_10_parser)

        assert cfg.value == 10

    @patch.object(EnvValue, "getter", MagicMock(return_value=(1, 2)))
    def test_raises_if_parser_failed(self) -> None:
        msg = re.escape("'key' could not parse '(1, 2)'")

        cfg = EnvValue("key", parser=int)

        with pytest.raises(ConfigValueParsingFailed, match=msg):
            cfg.value  # pylint: disable=pointless-statement

    @patch.dict(environ, {"RANDOM_VAR": "12"})
    def test_gets_value_from_env_with_int_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=int)

        assert env_cfg.value == 12

    @patch.dict(environ, {"RANDOM_VAR": "12"})
    def test_gets_value_from_env_with_list_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=list)

        assert env_cfg.value == ["1", "2"]

    @patch.dict(environ, {"RANDOM_VAR": '{"test": "ttt"}'})
    def test_gets_value_from_env_with_json_parser(self) -> None:
        env_cfg = EnvValue("RANDOM_VAR", parser=json.loads)

        assert env_cfg.value == {"test": "ttt"}

    @patch.dict(environ, {"RANDOM_VAR": "not-none"})
    def test_reset_sets_value_to_none_forcing_fetching_it_once_again(self) -> None:
        env_cfg = EnvValue[str]("RANDOM_VAR")
        assert env_cfg.value == "not-none"

        env_cfg.reset()

        with patch.dict(environ, {"RANDOM_VAR": "still-not-none"}):
            env_cfg = EnvValue[str]("RANDOM_VAR")
            assert env_cfg.value == "still-not-none"


class TestEnvConfig:
    @patch.dict(environ, {"RANDOM_VAR": "12.2.1"})
    def test_gets_value_from_env(self) -> None:
        env_cfg = EnvValue[str]("RANDOM_VAR")

        assert env_cfg.value == "12.2.1"


class TestSSMConfig:
    @patch.object(SSM, "get_parameter", autospec=True)
    def test_getter_calls_ssm_with_specific_key(self, mocked_get_parameter: MagicMock) -> None:
        mocked_get_parameter.return_value = "test_value"
        cfg = SSMValue[str]("key_name")

        assert cfg.value == "test_value"

        mocked_get_parameter.assert_called_once_with("key_name")


class TestConfigParser:
    def test_split_by_comma_returns_list(self) -> None:
        assert ConfigParser.split_by_comma("a,b") == ["a", "b"]

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ("1", True),
            ("true", True),
            ("TRUE", True),
            ("TruE", True),
            ("0", False),
            ("False", False),
            ("fLase", False),
            ("not-true", False),
            ("N/A", False),
            ("xxxxx", False),
        ],
    )
    def test_cast_to_bool_returns_bool(self, input_value: str, expected_value: bool) -> None:
        assert ConfigParser.cast_to_bool(input_value) == expected_value

    def test_load_jwt_keys_return_value_of_keys(self) -> None:
        assert ConfigParser.load_jwt_keys('{"keys": [{"key": "a"}]}') == [{"key": "a"}]
