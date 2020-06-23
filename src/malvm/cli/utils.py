"""This module contains helper methods related to the CLI."""
import click


def print_warning(text: str) -> None:
    click.echo(click.style(f"WARNING: {text}", bg="magenta", fg="black"))
