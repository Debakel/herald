"""Typer-based CLI for Herald."""

import logging
from pathlib import Path

import typer

from herald.config import ConfigError, PublisherBuilder

app = typer.Typer(
    name="herald",
    help="Reads events from iCal files and publishes formatted summaries to multiple targets.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def main(
    config: Path = typer.Option(
        "config.yaml", "--config", "-c", help="Path to config file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Increase log verbosity"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print output instead of publishing"
    ),
):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    if not config.exists():
        typer.echo(f"Error: Config file not found: {config}", err=True)
        raise typer.Exit(code=1)

    try:
        publisher = PublisherBuilder.from_config_file(config)
    except ConfigError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if dry_run:
        from herald.publish import TargetEntry
        from herald.targets.dryrun import DryRunTarget

        publisher.entries = [
            TargetEntry(DryRunTarget(name=e.target.__class__.__name__), e.template)
            for e in publisher.entries
        ]

    publisher.publish()


if __name__ == "__main__":
    app()
