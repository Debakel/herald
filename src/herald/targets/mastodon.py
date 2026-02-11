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
        """Publish a message to Mastodon."""
        self.client.status_post(message)
