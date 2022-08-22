import json
from os import environ
from unittest.mock import MagicMock, mock_open, patch

from lbz.configuration import SSM, BaseConfig, EnvConfig, JSONFileConfig, KeyValueConfig, SSMConfig


class TestEnvConfig:
    @patch.dict(environ, {"RANDOM_VAR": "12.2.1"}, clear=True)
    def test_gets_value_from_env(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR")

        assert env_cfg.get_value() == "12.2.1"

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_int_parser(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR", parser=int)

        assert env_cfg.get_value() == 12

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_list_parser(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR", parser=list)

        assert env_cfg.get_value() == ["1", "2"]

    @patch.dict(environ, {"RANDOM_VAR": '{"test": "ttt"}'}, clear=True)
    def test_gets_value_from_env_with_json_parser(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR", parser=json.loads)

        assert env_cfg.get_value() == {"test": "ttt"}


class TestBaseConfig:
    def test_returns_none_when_no_value_set(self) -> None:
        cfg = BaseConfig("test")  # type: ignore

        assert cfg.get_value() is None


class TestKeyValueConfig:
    def test_returns_value(self) -> None:
        cfg = KeyValueConfig("test", "test_value")

        assert cfg.get_value() == "test_value"


class TestSSMConfig:
    @patch.object(SSM, "get_parameter")
    def test_getter_calls_ssn_with_specific_key(self, mocked_get_parameter: MagicMock) -> None:
        cfg = SSMConfig("test", "path/to/key")

        cfg.get_value()

        mocked_get_parameter.assert_called_once_with(cfg.ssm_key)


class TestJSONFileConfig:
    @patch("builtins.open", mock_open(read_data='{"test": "ttt"}'))
    def test_getter_gets_value_from_file(self) -> None:
        cfg = JSONFileConfig("test", "./test.json")

        value = cfg.get_value()

        assert value == "ttt"

    @patch("builtins.open", mock_open(read_data='{"other": "ttt"}'))
    def test_getter_gets_value_from_file_using_diffrent_key(self) -> None:
        cfg = JSONFileConfig("test", "./test.json", json_key="other")

        value = cfg.get_value()

        assert value == "ttt"
