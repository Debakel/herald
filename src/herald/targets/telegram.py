"""Telegram target adapter."""

from typing import Literal

import telegram

from .base import Target


class TelegramTarget(Target):
    """Telegram publishing target."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        parse_mode: Literal["HTML", "Markdown", "MarkdownV2"] = "HTML",
    ):
        """Initialize the Telegram target.

        Args:
            bot_token: The Telegram bot token.
            chat_id: The chat ID to send messages to.
            parse_mode: Message parse mode (Markdown, HTML).
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.parse_mode = parse_mode

    def publish(self, message: str):
        """Publish a message to Telegram."""
        bot = telegram.Bot(token=self.bot_token)
        bot.send_message(chat_id=self.chat_id, text=message, parse_mode=self.parse_mode)
