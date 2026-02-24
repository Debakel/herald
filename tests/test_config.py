"""Tests for configuration loading, validation, and Publisher construction."""

from datetime import timedelta

import pytest

from herald.config import ConfigError, HeraldConfig, PublisherBuilder
from herald.targets.mastodon import MastodonTarget
from herald.targets.telegram import TelegramTarget
from tests.tempfile import TemporaryTextFile


class TestBuildPublisher:
    def test_build(self) -> None:
        with TemporaryTextFile("template 123") as template:
            cfg = HeraldConfig(
                source="/tmp/cal.ics",
                lookahead_window="30m",
                targets=[
                    {
                        "type": "mastodon",
                        "template": template.name,
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
        assert publisher.lookahead == timedelta(minutes=30)
        assert len(publisher.entries) == 2
        assert publisher.entries[0].template == "template 123"
        assert publisher.entries[1].template == "template 123"
        assert isinstance(publisher.entries[0].target, MastodonTarget)
        assert isinstance(publisher.entries[1].target, TelegramTarget)
        assert publisher.entries[1].target.bot_token == "bot-tok"

    def test_unknown_target_type(self) -> None:
        with TemporaryTextFile("tpl") as template:
            cfg = HeraldConfig(
                source="/tmp/cal.ics",
                lookahead_window="24h",
                targets=[{"type": "slack", "template": template.name, "config": {}}],
            )

            with pytest.raises(ConfigError, match="Unknown target type 'slack'"):
                PublisherBuilder.from_config(cfg)

    def test_post_mode_passed_to_entry(self) -> None:
        with TemporaryTextFile("tpl") as template:
            cfg = HeraldConfig(
                source="/tmp/cal.ics",
                lookahead_window="24h",
                targets=[
                    {
                        "type": "dryrun",
                        "template": template.name,
                        "post_mode": "single",
                        "config": {"name": "test"},
                    },
                ],
            )

            publisher = PublisherBuilder.from_config(cfg)

        assert publisher.entries[0].post_mode == "single"

    def test_post_mode_defaults_to_grouped(self) -> None:
        with TemporaryTextFile("tpl") as template:
            cfg = HeraldConfig(
                source="/tmp/cal.ics",
                lookahead_window="24h",
                targets=[
                    {
                        "type": "dryrun",
                        "template": template.name,
                        "config": {"name": "test"},
                    },
                ],
            )

            publisher = PublisherBuilder.from_config(cfg)

        assert publisher.entries[0].post_mode == "grouped"
