"""Tests for Mastodon target chunking behavior."""

from herald.targets.mastodon import _split_message


class TestSplitMessage:
    def test_short_message_unchanged(self):
        assert _split_message("hello", limit=100) == ["hello"]

    def test_exactly_500_chars_unchanged(self):
        msg = "a" * 5
        assert _split_message(msg, 5) == [msg]

    def test_splits_on_newline(self):
        line1 = "a" * 3
        line2 = "b" * 3
        msg = f"{line1}\n{line2}"
        assert _split_message(msg, 5) == [line1, line2]

    def test_splits_on_space(self):
        word1 = "a" * 3
        word2 = "b" * 3
        msg = f"{word1} {word2}"
        assert _split_message(msg, 5) == [word1, word2]

    def test_hard_split_when_no_boundary(self):
        msg = "a" * 7
        chunks = _split_message(msg, 5)
        assert chunks == ["a" * 5, "a" * 2]

    def test_multiple_chunks(self):
        msg = "a" * 15
        chunks = _split_message(msg, 5)
        assert chunks == ["a" * 5, "a" * 5, "a" * 5]

    def test_empty_message(self):
        assert _split_message("", 5) == [""]

    def test_prefers_newline_over_space(self):
        # Both newline and space available; should prefer newline
        part1 = "hello world"
        part2 = "b" * 9
        msg = f"{part1}\n{part2}"
        chunks = _split_message(msg, limit=20)
        assert chunks[0] == part1
        assert chunks[1] == part2
