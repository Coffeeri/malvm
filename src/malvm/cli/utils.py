"""This module contains helper methods related to the CLI."""

import click

from malvm.utils.logging import logger


def print_info(text: str) -> None:
    click.secho(f"{text}")
    logger.info(click.unstyle(text))


def print_warning(text: str) -> None:
    click.secho(f"WARNING: {text}", fg="yellow")
    logger.warning((click.unstyle(text)))


def print_error(text: str) -> None:
    click.secho(f"ERROR: {text}", fg="red")
    logger.error((click.unstyle(text)))
