"""This module is the entrypoint for the commandline."""
import click

from .malvm.main import check, fix, show, clean
from .packer.vm_builder import box


@click.group()
def malvm():
    """Base CLI-command for malvm."""


malvm.add_command(show)
malvm.add_command(clean)
malvm.add_command(check)
malvm.add_command(fix)
malvm.add_command(box)
