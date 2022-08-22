from os import environ
from unittest.mock import patch

import pytest

from lbz.configuration import (
    EnvConfig,
    KeyValueConfig,
    LazyLoadConfigManager,
    PreLoadConfigManager,
)
from lbz.exceptions import ConfigurationMissingKey


@patch.dict(environ, {"RANDOM_VAR": "12.2.1"}, clear=True)
class TestPreLoadConfigManager:
    def test_configs_are_validated_during_init_success(self) -> None:
        cfg_mng = PreLoadConfigManager(
            [
                EnvConfig("RANDOM_VAR"),
                KeyValueConfig("SECOND", 12),
            ]
        )
        assert cfg_mng.RANDOM_VAR == "12.2.1"
        assert cfg_mng.SECOND == 12

    def test_configs_are_validated_during_missing_config(self) -> None:
        with pytest.raises(ConfigurationMissingKey, match="Missing OTHER in configuration"):
            PreLoadConfigManager([EnvConfig("OTHER")])


@patch.dict(environ, {"RANDOM_VAR": "12.2.1"}, clear=True)
class TestLazyLoadConfigManager:
    def test_configs_are_accessible_by_attr(self) -> None:
        cfg_mng = LazyLoadConfigManager(
            [
                EnvConfig("RANDOM_VAR"),
                KeyValueConfig("SECOND", 12),
            ]
        )
        assert cfg_mng.RANDOM_VAR == "12.2.1"
        assert cfg_mng.SECOND == 12

    def test_validate_raises_when_missing_config(self) -> None:
        cfg_mngr = LazyLoadConfigManager([EnvConfig("OTHER")])
        with pytest.raises(ConfigurationMissingKey, match="Missing OTHER in configuration"):
            cfg_mngr.validate()
