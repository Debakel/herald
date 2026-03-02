"""Configuration loading, validation, and Publisher construction."""
from datetime import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel

from herald.domain.window import TimeWindow, WindowParseError, parse_window
from herald.publish import Publisher, PublishMode, TargetEntry
from herald.targets.registry import target_registry

__all__ = ["ConfigError", "PublisherBuilder"]


class ConfigError(Exception): ...


class HeraldConfig(BaseModel):
    source: str
    window: "WindowConfig"
    targets: list["TargetConfig"]


class WindowConfig(BaseModel):
    after: str = "0m"
    before: str

    def as_timewindow(self) -> TimeWindow:
        now = datetime.now()
        try:
            after = parse_window(self.after)
            before = parse_window(self.before)
        except WindowParseError as e:
            raise ConfigError(str(e)) from e

        return TimeWindow(start=now + after, end=now + before)


class TargetConfig(BaseModel):
    type: str
    template: Path
    publish_mode: PublishMode = PublishMode.GROUPED
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
            entries.append(
                TargetEntry(
                    target=target,
                    template=template,
                    publish_mode=tc.publish_mode,
                )
            )

        return Publisher(
            source=config.source,
            entries=entries,
            time_window=config.window.as_timewindow()
        )
