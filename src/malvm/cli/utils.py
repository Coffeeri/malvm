"""This module contains helper methods related to the CLI."""
import logging
from typing import Optional

import click

log = logging.getLogger()


def print_info(text: str, command: Optional[str] = "") -> None:
    click.secho(f"{text}")
    log.error("lolo")
    command_message = f"COMMAND: {command}\nOUTPUT: "
    log.debug(f"{command_message if command else ''}"
              f"{click.unstyle(text)}")


def print_warning(text: str) -> None:
    click.secho(f"WARNING: {text}", fg="yellow")
    log.warning((click.unstyle(text)))
