"""This module contains the CLI for the malboxes-tool."""

import re
import subprocess
from pathlib import Path
from typing import List
import click
import inquirer  # type: ignore


def malboxes_list() -> List[str]:
    """Returns list of all possible malbox templates."""
    malboxes_process = subprocess.run(
        ["malboxes", "list"], stdout=subprocess.PIPE, check=True
    )
    malboxes_return = malboxes_process.stdout.decode("utf-8")
    regex = re.compile(r"\S*_analyst")
    match: List[str] = regex.findall(malboxes_return)
    if match:
        return match
    raise ProcessLookupError(
        "Malboxes could not be found. \n"
        "Make sure to install Malboxes and have a working \n"
        "internet connection."
    )


MALBOX_TEMPLATE_CHOICES = malboxes_list()


@click.group(chain=True)
def box():
    """Handles Malboxes."""


@box.command()
@click.argument("template", type=click.Choice(MALBOX_TEMPLATE_CHOICES), required=False)
def build(template: str):
    """Builds a Malbox template."""
    if not template:
        questions = [
            inquirer.List(
                "malbox-template",
                message="What malebox template should be installed?",
                choices=MALBOX_TEMPLATE_CHOICES,
            ),
        ]
        template = inquirer.prompt(questions)["malbox-template"]
    click.clear()
    click.echo(
        click.style(
            f"> Building template {click.style(template, fg='yellow')}:", fg="green"
        )
    )
    subprocess.run(["malboxes", "build", template], check=True)


@box.command()
@click.argument(
    "template", type=click.Choice(MALBOX_TEMPLATE_CHOICES),
)
@click.argument("name")
def run(template, name):
    """Run TEMPLATE as NAME in Virtualbox via Vagrant.

    TEMPLATE is the in `malvm box build` build template.
    NAME is the selected name of the VM spun up in VirtualBox.

    Examples:

        $ malvm box run win7_x86_analyst 20160519.cryptolocker.xyz
    """
    click.echo(
        click.style(
            f"> Spin up VM {click.style(name, fg='yellow')} "
            f"with template {click.style(template, fg='yellow')}:",
            fg="green",
        )
    )
    subprocess.run(["malboxes", "spin", template, name], check=True)

    if not Path("Vagrantfile").exists():
        click.echo(
            click.style(
                "> Vagrantfile does not exist. "
                "Please use `malvm box build` to generate one.",
                fg="red",
            )
        )
    else:
        subprocess.run(["vagrant", "up"], check=True)
