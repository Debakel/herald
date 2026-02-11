from herald.targets import Target


class DryRunTarget(Target):
    """A mock target for dry-run mode that prints instead of publishing."""

    def __init__(self, name: str) -> None:
        self.name = name

    def publish(self, message: str) -> None:
        """Print the message that would be published."""
        print(f"{self.name}: {message}")
