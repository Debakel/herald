"""Base protocol for publishing targets."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Target(Protocol):
    """Protocol for publishing targets.

    All target adapters must implement this interface.
    """

    def publish(self, message: str) -> None:
        """Publish a message to this target.

        Args:
            message: The rendered message to publish.
        """
        ...


class FakeTarget(Target):
    """Fake target for testing."""

    def __init__(self):
        self.published_messages = []

    def publish(self, message: str) -> None:
        self.published_messages.append(message)
