from typing import Any, Dict, List

from lbz.configuration.configs import BaseConfig
from lbz.exceptions import ConfigurationMissingKey


class PreLoadConfigManager:
    def __init__(self, configs: List[BaseConfig]) -> None:
        self.configs: Dict[str, Any] = {}
        for cfg in configs:
            value = cfg.get_value()
            if value is cfg.default is None:
                raise ConfigurationMissingKey(cfg.key)
            self.configs[cfg.key] = value

    def __getattr__(self, item: str) -> Any:
        return self.configs[item]


class LazyLoadConfigManager:
    def __init__(self, configs: List[BaseConfig]) -> None:
        self.configs: Dict[str, BaseConfig] = {cfg.key: cfg for cfg in configs}

    def __getattr__(self, item: str) -> Any:
        try:
            cfg = self.configs[item]
            return cfg.get_value()
        except KeyError:
            raise ConfigurationMissingKey(item) from KeyError

    def validate(self) -> None:
        for cfg in self.configs.values():
            value = cfg.get_value()
            if value is cfg.default is None:
                raise ConfigurationMissingKey(cfg.key)
