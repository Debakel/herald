"""Target adapters for publishing."""

from .base import Target
from .mastodon import MastodonTarget
from .telegram import TelegramTarget

__all__ = [
    "MastodonTarget",
    "Target",
    "TelegramTarget",
]
