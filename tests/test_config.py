"""Tests for configuration loading, validation, and Publisher construction."""

from datetime import datetime

import pytest

import freezegun

from herald.config import ConfigError, HeraldConfig, PublisherBuilder, WindowConfig
from herald.publish import PublishMode
from herald.targets.mastodon import MastodonTarget
from herald.targets.telegram import TelegramTarget
from tests.tempfile import TemporaryTextFile


class TestBuildPublisher:
    @freezegun.freeze_time("2026-02-03 08:00")
    def test_build(self) -> None:
        with TemporaryTextFile("template 123") as template:
            cfg = HeraldConfig(
                source="/tmp/cal.ics",
                window={"before": "30m"},
                targets=[
                    {
                        "type": "mastodon",
                        "template": template.name,
                        "publish_mode": PublishMode.SINGLE,
                        "config": {
                            "instance_url": "https://a.social",
                            "access_token": "tok-a",
                            "client_id": "123",
                            "client_secret": "secret",

                        },
                    },
                    {
                        "type": "telegram",
                        "template": template.name,
                        "config": {
                            "bot_token": "bot-tok",
                            "chat_id": "999",
                            "parse_mode": "HTML",
                        },
                    },
                ],
            )

            publisher = PublisherBuilder.from_config(cfg)

        assert publisher.source == "/tmp/cal.ics"
        assert publisher.time_window.start == datetime(2026, 2, 3, 8, 0)
        assert publisher.time_window.end == datetime(2026, 2, 3, 8, 30)
        assert len(publisher.entries) == 2

        assert publisher.entries[0].template == "template 123"
        assert publisher.entries[0].publish_mode == PublishMode.SINGLE
        assert isinstance(publisher.entries[0].target, MastodonTarget)


        assert publisher.entries[1].template == "template 123"
        assert publisher.entries[1].publish_mode == PublishMode.GROUPED
        assert isinstance(publisher.entries[1].target, TelegramTarget)
        assert publisher.entries[1].target.bot_token == "bot-tok"

    def test_unknown_target_type(self) -> None:
        with TemporaryTextFile("tpl") as template:
            cfg = HeraldConfig(
                source="/tmp/cal.ics",
                window={"before": "24h"},
                targets=[{"type": "slack", "template": template.name, "config": {}}],
            )

            with pytest.raises(ConfigError, match="Unknown target type 'slack'"):
                PublisherBuilder.from_config(cfg)


class TestWindowConfig:
    @freezegun.freeze_time("2026-02-03 08:00")
    def test_as_timewindow(self) -> None:
        window = WindowConfig(before="30m")
        time_window = window.as_timewindow()

        assert time_window.start == datetime(2026, 2, 3, 8, 0)
        assert time_window.end == datetime(2026, 2, 3, 8, 30)
