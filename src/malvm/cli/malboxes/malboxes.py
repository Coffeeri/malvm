"""This module contains the CLI for the malboxes-tool."""

import re
import subprocess
import sys
from pathlib import Path
from platform import system
from typing import List
import click
import inquirer  # type: ignore

from ...utils.helper_methods import get_project_root


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
    update_malboxes_config()
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
    subprocess.run(["malboxes", "build", "--force", template], check=True)


def update_malboxes_config() -> None:
    """Inserts custom malbox config."""
    click.echo("> Update Malboxes config.")
    if system() == "Linux":
        Path(get_project_root() / "data/malboxes_config.js").replace(
            Path.home() / ".config/malboxes/config.js"
        )
    else:
        click.echo(
            click.style(
                "Sorry, currently Linux is the only supported platform.", bg="red"
            )
        )
        sys.exit(1)


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

    if not Path("Vagrantfile").exists():
        click.echo(click.style("> Vagrantfile does not exist.", fg="red",))

        click.echo(
            click.style(
                f"> Spin up VM {click.style(name, fg='yellow')} "
                f"with template {click.style(template, fg='yellow')}:",
                fg="green",
            )
        )
        subprocess.run(["malboxes", "spin", template, name], check=True)
        add_provisioning_vagrantfile()
    subprocess.run(["vagrant", "up"], check=True)


def add_provisioning_vagrantfile() -> None:
    """Adds provisioning for malvm into Vagrantfile."""
    additional_provisioning = """
    # Install choco, python and git
    config.vm.provision "shell", privileged: "true", powershell_elevated_interactive: "true", inline: <<-SHELL
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    choco install python3 git -y
    SHELL
    
    # Install malvm
    config.vm.provision "shell", privileged: "true", powershell_elevated_interactive: "true", inline: <<-SHELL
    cd C:/Users/max/Desktop/host/
    pip install -r requirements.txt
    python setup.py install
    malvm fix
    SHELL
end
    """  # noqa: E501, W293
    append_to_vagrantfile(additional_provisioning)


def append_to_vagrantfile(text: str) -> None:
    """Removes last line and appends text to Vagrantfile."""
    with Path("Vagrantfile").open(mode="r") as file:
        lines = file.readlines()
        lines = lines[:-1]
    with Path("Vagrantfile").open(mode="w+") as file:
        lines.append(text)
        file.writelines(lines)
