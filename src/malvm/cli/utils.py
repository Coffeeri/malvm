"""This module contains helper methods related to the CLI."""
import sys
from typing import Optional

import click

from malvm.utils.logging import logger


def print_info(text: str, command: Optional[str] = "") -> None:
    click.secho(f"{text}")
    command_message = f"COMMAND: {command}\nOUTPUT: "
    logger.debug(f"{command_message if command else ''}"
                 f"{click.unstyle(text)}")


def print_warning(text: str) -> None:
    click.secho(f"WARNING: {text}", fg="yellow")
    logger.warning((click.unstyle(text)))


def print_error(text: str) -> None:
    click.secho(f"ERROR: {text}", fg="red")
    logger.error((click.unstyle(text)))


def print_critical_error(text: str) -> None:
    click.secho(f"ERROR: {text}", fg="red")
    logger.critical((click.unstyle(text)))
    sys.exit(1)
