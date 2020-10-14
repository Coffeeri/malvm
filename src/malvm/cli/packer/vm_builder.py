"""This module contains the CLI for creating sanitized windows virtual machines."""

import os
import subprocess
from pathlib import Path

import click
import inquirer  # type: ignore

from ...utils.helper_methods import get_data_dir
from ..utils import print_warning
from .box_template import BoxConfiguration, PackerTemplate

PACKER_PATH = get_data_dir() / "packer"


WIN_10_CONFIG = BoxConfiguration(
    packer_template_path=(PACKER_PATH / "windows_10.json"),
    packer_box_name="windows_10_virtualbox.box",
    vagrant_box_name="win-10",
    username="max",
    password="123456",
    computer_name="Computer",
    language_code="de-De",
)

BOX_TEMPLATES = {"windows_10": WIN_10_CONFIG}
BOX_TEMPLATE_CHOICES = list(BOX_TEMPLATES.keys())


@click.group(chain=True)
def box():
    """Handles Malboxes."""


@box.command()
@click.argument("template", type=click.Choice(BOX_TEMPLATE_CHOICES), required=False)
def build(template: str):
    """Builds a Malbox template."""
    print_warning("Note: Currently only Windows 10 box implemented.")
    if not template:
        questions = [
            inquirer.List(
                "box-template",
                message="What Windows box template should be build?",
                choices=BOX_TEMPLATE_CHOICES,
            ),
        ]
        template = inquirer.prompt(questions)["box-template"]
    click.clear()
    click.echo(
        click.style(
            f"> Building template {click.style(template, fg='yellow')}:", fg="green"
        )
    )
    template_config = BOX_TEMPLATES[template]
    packer_template = PackerTemplate(template, template_config)
    packer_template.configure()
    packer_template.build()
    packer_template.add_to_vagrant()


@box.command()
@click.argument(
    "template", type=click.Choice(BOX_TEMPLATE_CHOICES),
)
@click.argument("name")
@click.option("-o", "--output", show_default=True, default=str(Path.cwd().absolute()))
def run(template, name, output: str):
    """Run TEMPLATE as NAME in Virtualbox via Vagrant.

    TEMPLATE is the in `malvm box build` build template.
    NAME is the selected name of the VM spun up in VirtualBox.

    Examples:

        $ malvm box run windows_10 win10-vm01
    """
    if not Path("Vagrantfile").exists():
        click.echo(click.style("> Vagrantfile does not exist.", fg="red",))
        click.echo(
            click.style(
                f"> Spin up [{click.style(template, fg='yellow')}] VM "
                f"{click.style(name, fg='yellow')}...",
                fg="green",
            )
        )
        PackerTemplate(template, BOX_TEMPLATES[template]).setup_virtualmachine(
            name, Path(output)
        )
    else:
        os.chdir(output)
        subprocess.run(
            ["vagrant", "up"], check=True,
        )
    click.echo(
        click.style(
            f"VM {name} was started. "
            f"A snapshot of the ´clean-state´ was saved.\n"
            f"Don't shutdown the VM, prefer to use these commands:\n\n"
            f"Stop VM:  `vagrant suspend`\n"
            f"Start VM: `vagrant resume` or \n"
            f"          `vagrant up`\n"
            f"Reset VM: `vagrant snapshot restore clean-state`\n\n"
            f"If you need to run `malvm fix` again in an elevated cmd, "
            f"please run on the host:\n"
            f"$ vagrant winrm -e -c malvm fix"
            f"This will run the malvm in an shell with elevated privileges.",
            fg="green",
        )
    )
