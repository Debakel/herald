import os
import tempfile
from typing import Self


class TemporaryTextFile:
    """Create and return a temporary text file."""

    def __init__(self, text: str = ""):
        self.file = tempfile.NamedTemporaryFile(delete=False, mode="wt")
        self.file.write(text)
        self.file.flush()
        self.file.seek(0)

    @property
    def name(self):
        return self.file.name

    def delete(self) -> None:
        os.remove(self.file.name)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()
