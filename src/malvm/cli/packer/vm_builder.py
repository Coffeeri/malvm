"""This module contains the CLI for creating sanitized windows virtual machines."""

import os
import subprocess
import sys
from pathlib import Path

import click
import inquirer  # type: ignore

from ...utils.helper_methods import (
    get_data_dir,
    add_vm_to_vagrant_files, get_vm_malvm_package_file, get_config_root,
    get_vagrantfiles_folder_path, get_vm_ids_dict,
)
from ..utils import print_warning
from .box_template import BoxConfiguration, PackerTemplate

PACKER_PATH = get_data_dir() / "packer"

WIN_10_CONFIG = BoxConfiguration(
    packer_template_path=(PACKER_PATH / "windows_10.json"),
    packer_box_name="windows_10_virtualbox.box",
    vagrant_box_name="malvm-win-10",
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
    check_needed_files()
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


def check_needed_files():
    if not get_vm_malvm_package_file().exists():
        print("Error: Malvm.tar.gz was not found.\n"
              "Please consider reinstalling with:\n"
              "Run `malvm clean` and `source bootstrap.sh`")
        sys.exit(1)


@box.command()
@click.argument(
    "template", type=click.Choice(BOX_TEMPLATE_CHOICES),
)
@click.argument("name")
def run(template, name):
    """Run TEMPLATE as NAME in Virtualbox via Vagrant.

    TEMPLATE is the in `malvm box build` build template.
    NAME is the selected name of the VM spun up in VirtualBox.

    Examples:

        $ malvm box run windows_10 win10-vm01
    """
    vagrantfile_path = get_vagrantfiles_folder_path() / name
    if not (vagrantfile_path / "Vagrantfile").exists():
        vagrantfile_path.mkdir(parents=True, exist_ok=True)
        click.echo(click.style(f"> Vagrantfile for {name} does not exist. ✓", fg="green", ))
        click.echo(
            click.style(
                f"> Spin up [{click.style(template, fg='yellow')}] VM "
                f"{click.style(name, fg='yellow')}...",
                fg="green",
            )
        )

        PackerTemplate(template, BOX_TEMPLATES[template]).setup_virtualmachine(
            name, vagrantfile_path
        )
    else:
        os.chdir(vagrantfile_path)
        subprocess.run(
            ["vagrant", "up"], check=True,
        )
    add_vm_to_vagrant_files(name, vagrantfile_path)

    vm_id = get_vm_ids_dict()[name]
    click.echo(
        click.style(
            f"VM {name} was started. "
            f"A snapshot of the ´clean-state´ was saved.\n"
            f"Don't shutdown the VM, prefer to use these commands:\n\n"
            f"Stop VM:  `vagrant suspend {vm_id}`\n"
            f"Start VM: `vagrant resume {vm_id}` or \n"
            f"          `vagrant up {vm_id}`\n"
            f"Reset VM: `vagrant snapshot restore clean-state`\n\n"
            f"If you need to run `malvm fix` again in an elevated cmd, "
            f"please run on the host:\n"
            f"$ vagrant winrm -e -c malvm fix {vm_id}"
            f"This will run the malvm in an shell with elevated privileges.",
            fg="green",
        )
    )


@box.command()
@click.argument("name")
def stop(name: str):
    """Suspends virtual machine."""
    vm_id = get_vm_ids_dict()[name]
    subprocess.run(
        ["vagrant", "suspend", vm_id], check=True,
    )
