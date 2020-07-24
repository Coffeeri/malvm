"""This module is the entrypoint for the commandline."""
import click

from .packer.vm_builder import box
from .malvm.malvm import check, fix, show


@click.group()
def malvm():
    """Base CLI-command for malvm."""


malvm.add_command(show)
malvm.add_command(check)
malvm.add_command(fix)
malvm.add_command(box)
