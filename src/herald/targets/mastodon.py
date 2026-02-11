"""Mastodon target adapter."""

from mastodon import Mastodon

from .base import Target



class MastodonTarget(Target):
    """Mastodon publishing target."""

    def __init__(
        self,
        instance_url: str,
        client_id: str,
        client_secret: str,
        access_token: str,
    ) -> None:
        """Initialize the Mastodon target."""
        self.client = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=instance_url,
        )

    def publish(self, message: str) -> None:
        """Publish a message to Mastodon"""
        MAX_STATUS_LENGTH = 500
        chunks = _split_message(message, limit=MAX_STATUS_LENGTH)
        previous = None
        for chunk in chunks:
            previous = self.client.status_post(
                chunk,
                in_reply_to_id=previous,
            )


def _split_message(text: str, limit: int) -> list[str]:
    """Split a text into chunks that fit within the character limit.

    Splits on newline boundaries when possible, otherwise on word
    boundaries, and as a last resort mid-word.
    """
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        # Try newline boundary first, then space, then hard split
        nl = remaining.rfind("\n", 0, limit)
        if nl != -1:
            chunks.append(remaining[:nl])
            remaining = remaining[nl + 1 :]
        else:
            sp = remaining.rfind(" ", 0, limit)
            if sp != -1:
                chunks.append(remaining[:sp])
                remaining = remaining[sp + 1 :]
            else:
                chunks.append(remaining[:limit])
                remaining = remaining[limit:]

    return chunks
