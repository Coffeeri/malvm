"""This module is the entrypoint for the commandline."""
import click

from .. import __version__
from .malvm.main import check, fix, show, clean, up
from .box.vm_builder import box


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
