"""Configuration loading, validation, and Publisher construction."""

from pathlib import Path

import yaml
from pydantic import BaseModel

from herald.domain.window import parse_window
from herald.publish import Publisher, TargetEntry
from herald.targets.registry import target_registry

__all__ = ["ConfigError", "PublisherBuilder"]


class ConfigError(Exception): ...


class HeraldConfig(BaseModel):
    source: str
    lookahead_window: str
    targets: list["TargetConfig"]


class TargetConfig(BaseModel):
    type: str
    template: Path
    config: dict = {}


class PublisherBuilder:
    @staticmethod
    def from_config_file(file_path: Path) -> Publisher:
        with open(file_path) as f:
            raw = yaml.safe_load(f)

        if not isinstance(raw, dict):
            raise ConfigError("Config file must be a YAML mapping")

        config = HeraldConfig.model_validate(raw)
        return PublisherBuilder.from_config(config)

    @classmethod
    def from_config(cls, config: HeraldConfig) -> Publisher:
        """Construct a Publisher instance from a validated config."""

        entries: list[TargetEntry] = []

        for tc in config.targets:
            target_cls = target_registry.get(tc.type)
            if target_cls is None:
                raise ConfigError(f"Unknown target type '{tc.type}'")

            target = target_cls(**tc.config)
            template = tc.template.read_text()
            entries.append(TargetEntry(target=target, template=template))

        return Publisher(
            source=config.source,
            entries=entries,
            lookahead=parse_window(config.lookahead_window),
        )
