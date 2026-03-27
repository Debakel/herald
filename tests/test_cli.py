"""Tests for the herald CLI."""

import textwrap
import unittest
from pathlib import Path

from freezegun import freeze_time
from typer.testing import CliRunner

from herald.cli import app
from tests.tempfile import TemporaryTextFile


class CLITestCase(unittest.TestCase):
    def setUp(self):
        self.template_file_1 = TemporaryTextFile(
            text=textwrap.dedent("""
        {% for event in events %}
        - `{{ event.start }}` — {{ event.title }} (in {{ event.location }})
        {% endfor %}
        """)
        )
        self.template_file_2 = TemporaryTextFile(
            text="{{ event.title }}"
        )

        config = textwrap.dedent("""\
            source: {source}
            window:
              before: 14d
            targets:
              - type: dryrun
                template: {template_file_1}
                config:
                  name: target-1
              - type: dryrun
                template: {template_file_2}
                publish_mode: single
                config:
                  name: target-2
        """).format(
            source=Path(__file__).parent / "testdata/recurring-event.ics",
            template_file_1=self.template_file_1.name,
            template_file_2=self.template_file_2.name,
        )

        self.config_file = TemporaryTextFile(text=config)

    def tearDown(self):
        self.config_file.delete()
        self.template_file_1.delete()
        self.template_file_2.delete()

    @freeze_time("2026-02-01T12:00:00")
    def test_cli(self):
        runner = CliRunner()
        result = runner.invoke(app, ["--config", self.config_file.name])

        expected = ('target-1: \n'
                    '\n'
                    '- `2026-02-02 10:00:00+00:00` — Weekly Standup (in Virtual)\n'
                    '\n'
                    '- `2026-02-09 10:00:00+00:00` — Weekly Standup (in Virtual)\n'
                    '\n'
                    'target-2: Weekly Standup\n'
                    'target-2: Weekly Standup\n')
        self.assertEqual(result.output, expected)

        self.assertEqual(
            result.exit_code,
            0,
            msg={"exc_info": result.exc_info, "stdout": result.stdout},
        )
