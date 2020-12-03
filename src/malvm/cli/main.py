"""This module is the entrypoint for the commandline."""
import click
from pkg_resources import get_distribution
from .malvm.main import check, fix, show, clean
from .packer.vm_builder import box

__version__ = get_distribution('malvm').version


@click.group()
@click.version_option(__version__)
@click.pass_context
def malvm():
    """Base CLI-command for malvm."""


malvm.add_command(show)
malvm.add_command(clean)
malvm.add_command(check)
malvm.add_command(fix)
malvm.add_command(box)
