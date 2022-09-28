import json
from os import environ
from unittest.mock import MagicMock, patch

from lbz.configuration import SSM, BaseConfig, EnvConfig, KeyValueConfig, SSMConfig



class TestBaseConfig:
    @patch.object(BaseConfig, "getter", autospec=True)
    def test_if_getter_was_used(self, mocked_getter: MagicMock) -> None:
        cfg = BaseConfig("key") # type: ignore

        cfg.get_value()

        mocked_getter.assert_called_once()

    def test_returns_none_when_no_value_set(self) -> None:
        cfg = BaseConfig("test")  # type: ignore

        assert cfg.get_value() is None

    def test_returns_default_when_no_value_set(self) -> None:
        cfg = BaseConfig("test", default=42)  # type: ignore

        assert cfg.get_value() == 42
        assert cfg.value == 42

    def test_if_parser_was_used(self) -> None:
        class MyBaseConfig(BaseConfig):
            def getter(self) -> int:
                return 1

        cfg = MyBaseConfig("key", parser=str)

        assert cfg.get_value() == "1"
        assert cfg.value == "1"

    @patch.object(BaseConfig, "getter", autospec=True)
    def test_if_getter_was_used_only_once(self, mocked_getter: MagicMock) -> None:
        mocked_getter.return_value = 42
        cfg = BaseConfig("key") # type: ignore

        assert cfg.get_value() == 42
        assert cfg.get_value() == 42

        mocked_getter.assert_called_once()


class TestEnvConfig:
    @patch.dict(environ, {"RANDOM_VAR": "12.2.1"}, clear=True)
    def test_gets_value_from_env(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR")

        assert env_cfg.value == "12.2.1"

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_int_parser(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR", parser=int)

        assert env_cfg.get_value() == 12
        assert env_cfg.value == 12

    @patch.dict(environ, {"RANDOM_VAR": "12"}, clear=True)
    def test_gets_value_from_env_with_list_parser(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR", parser=list)

        assert env_cfg.get_value() == ["1", "2"]
        assert env_cfg.value == ["1", "2"]

    @patch.dict(environ, {"RANDOM_VAR": '{"test": "ttt"}'}, clear=True)
    def test_gets_value_from_env_with_json_parser(self) -> None:
        env_cfg = EnvConfig("RANDOM_VAR", parser=json.loads)

        assert env_cfg.get_value() == {"test": "ttt"}
        assert env_cfg.value == {"test": "ttt"}




class TestKeyValueConfig:
    def test_returns_value(self) -> None:
        cfg = KeyValueConfig("test_value")

        assert cfg.get_value() == "test_value"
        assert cfg.value == "test_value"


class TestSSMConfig:
    @patch.object(SSM, "get_parameter")
    def test_getter_calls_ssn_with_specific_key(self, mocked_get_parameter: MagicMock) -> None:
        mocked_get_parameter.return_value = "test_value"
        cfg = SSMConfig("path/to/key")

        assert cfg.get_value() == "test_value"
        assert cfg.value == "test_value"

        mocked_get_parameter.assert_called_once_with(cfg.key)
