"""This module is the entrypoint for the commandline."""
import click

from .. import __version__
from .box.vm_builder import box
from .malvm.main import check, clean, fix, show, up


@click.group()
@click.version_option(__version__)
def malvm():
    """Base CLI-command for malvm."""


malvm.add_command(show)
malvm.add_command(clean)
malvm.add_command(check)
malvm.add_command(fix)
malvm.add_command(box)
malvm.add_command(up)
