"""Window parsing and time range calculation."""

from dataclasses import dataclass
import re
from datetime import datetime, timedelta


class WindowParseError(ValueError):
    """Raised when a window specification cannot be parsed."""

@dataclass(frozen=True)
class TimeWindow:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("'end' must be greater than 'start'")



def parse_window(window_spec: str) -> timedelta:
    """Parse a window specification string into a timedelta.

    Supported formats:
    - "24h" for hours
    - "7d" for days
    - "1m" for minutes

    Args:
        window_spec: The window specification string.

    Returns:
        A timedelta representing the window duration.

    Raises:
        WindowParseError: If the specification cannot be parsed.
    """
    pattern = r"^(\d+)([hdm])$"
    match = re.match(pattern, window_spec.strip().lower())

    if not match:
        raise WindowParseError(
            f"Invalid window specification: '{window_spec}'. "
            "Expected format like '24h', '7d', or '1m'."
        )

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "m":
        return timedelta(minutes=value)
    else:
        raise WindowParseError(f"Unknown time unit: '{unit}'")
