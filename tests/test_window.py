"""Tests for window parsing and time range calculation."""

from datetime import datetime, timedelta

import pytest

from herald.domain import TimeWindow, WindowParseError, parse_window


class TestParseWindow:
    """Tests for parse_window function."""

    def test_parse_hours(self) -> None:
        """Test parsing hour specifications."""
        assert parse_window("24h") == timedelta(hours=24)
        assert parse_window("1h") == timedelta(hours=1)
        assert parse_window("48h") == timedelta(hours=48)

    def test_parse_days(self) -> None:
        """Test parsing day specifications."""
        assert parse_window("7d") == timedelta(days=7)
        assert parse_window("1d") == timedelta(days=1)
        assert parse_window("30d") == timedelta(days=30)

    def test_parse_minutes(self) -> None:
        """Test parsing minute specifications."""
        assert parse_window("0m") == timedelta(minutes=0)
        assert parse_window("1m") == timedelta(minutes=1)
        assert parse_window("30m") == timedelta(minutes=30)
        assert parse_window("90m") == timedelta(minutes=90)

    def test_parse_case_insensitive(self) -> None:
        """Test that parsing is case insensitive."""
        assert parse_window("24H") == timedelta(hours=24)
        assert parse_window("7D") == timedelta(days=7)
        assert parse_window("30M") == timedelta(minutes=30)

    def test_parse_with_whitespace(self) -> None:
        """Test that leading/trailing whitespace is ignored."""
        assert parse_window("  24h  ") == timedelta(hours=24)

    def test_invalid_format_raises_error(self) -> None:
        """Test that invalid formats raise WindowParseError."""
        with pytest.raises(WindowParseError):
            parse_window("invalid")

        with pytest.raises(WindowParseError):
            parse_window("24")

        with pytest.raises(WindowParseError):
            parse_window("h24")

        with pytest.raises(WindowParseError):
            parse_window("24x")

        with pytest.raises(WindowParseError):
            parse_window("")


class TestTimeWindow:
    def test_valid_window(self) -> None:
        start = datetime(2026, 2, 3, 8, 0)
        end = datetime(2026, 2, 3, 8, 30)
        tw = TimeWindow(start=start, end=end)

        assert tw.start == start
        assert tw.end == end

    def test_invalid_window(self) -> None:
        start = datetime(2026, 2, 3, 8, 0)
        end = datetime(2026, 2, 3, 8, 0)

        with pytest.raises(ValueError, match="'end' must be greater than 'start'"):
            TimeWindow(start=start, end=end)
