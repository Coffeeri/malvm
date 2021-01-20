"""This module contains the CLI for creating sanitized windows virtual machines."""
import logging
import os
import subprocess
import sys

import click
import inquirer  # type: ignore
from malvm.controller.config_loader import BaseImageSettings, BaseImagesType

from ..malvm.main import remove_vm_and_data
from ...controller import Controller
from ...utils.helper_methods import (
    get_data_dir,
    add_vm_to_vagrant_files, get_vm_malvm_package_file,
    get_vagrant_files_folder_path, get_vm_ids_dict,
    get_existing_vagrant_files_paths_iterable,
)
from ..utils import print_info
from .box_template import BoxConfiguration, PackerTemplate

controller = Controller()
log = logging.getLogger()
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


def check_missing_base_images():
    pass


@click.group(chain=True)
def box():
    """Handles Malboxes."""


def get_box_config_by_base_image_name(base_image_name: str) -> BoxConfiguration:
    base_images: BaseImagesType = controller.configuration.base_images
    return BoxConfiguration(
        packer_template_path=(PACKER_PATH / f"{base_images[base_image_name].template}.json"),
        packer_box_name=f"{base_images[base_image_name].template}_virtualbox.box",
        vagrant_box_name=base_image_name,
        username=base_images[base_image_name].username,
        password=base_images[base_image_name].password,
        computer_name=base_images[base_image_name].computer_name,
        language_code=base_images[base_image_name].language_code,
    )


@box.command()
@click.argument("template", type=click.Choice(BOX_TEMPLATE_CHOICES), required=False)
@click.argument("base_image_name", default="malvm-win-10")
def build(template: str, base_image_name: str):
    """Builds a Malbox template."""
    check_needed_files()
    box_config = get_box_config_by_base_image_name(base_image_name)
    log.warning("Currently only Windows 10 box implemented.")
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
    print_info(f"> Building template {click.style(template, fg='yellow')}...")
    log.debug(box_config)
    packer_template = PackerTemplate(template, box_config)
    packer_template.configure()
    packer_template.build()
    packer_template.add_to_vagrant()


def check_needed_files():
    if not get_vm_malvm_package_file().exists():
        log.error("Malvm.tar.gz was not found.\n"
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
    vagrantfile_path = get_vagrant_files_folder_path() / name
    if not (vagrantfile_path / "Vagrantfile").exists():
        vagrantfile_path.mkdir(parents=True, exist_ok=True)
        print_info(f"Vagrantfile for {name} does not exist. ✓",
                   command=f"malvm box run {template} {name}")
        print_info(
            f"> Spin up [{click.style(template, fg='yellow')}] VM "
            f"{click.style(name, fg='yellow')}..."
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

    print_info(
        f"VM {name} was started. "
        f"A snapshot of the ´clean-state´ was saved.\n"
        f"Don't shutdown the VM, prefer to use these commands:\n\n"
        f"Stop VM:  `malvm box stop {name}`\n"
        f"Start VM: `malvm box run {name}`\n"
        f"Reset VM: `malvm box reset {name}`\n"
        f"Remove VM: `malvm box remove {name}`\n\n"
        f"If you need to run `malvm fix` again in an elevated cmd, "
        f"please run on the host:\n"
        f"`malvm box fix {name}`"
        f"This will run the malvm in an shell with elevated privileges."
    )


@box.command()
@click.argument("name")
def stop(name: str):
    """Suspends virtual machine."""
    vm_id = get_vm_ids_dict()[name]
    print_info(f"Suspending VM {name}...",
               command=f"malvm box stop {name}")
    subprocess.run(
        ["vagrant", "suspend", vm_id], check=True,
    )


@box.command()
@click.argument("name")
def reset(name: str):
    """Resets virtual machine.

    Resetting by restoring the `clean-state` snapshot.
    """
    vm_id = get_vm_ids_dict()[name]
    print_info(f"Resetting VM {name}...",
               command=f"malvm box reset {name}")
    subprocess.run(
        ["vagrant", "snapshot", "restore", vm_id, "clean-state"], check=True,
    )


@box.command()
@click.argument("name")
def remove(name: str):
    """Removes virtual machine."""
    print_info(f"Destroying VM {name}...",
               command=f"malvm box remove {name}")
    remove_vm_and_data(name)


@box.command()
@click.argument("name")
def fix(name: str):
    """Runs fixes on virtual machine."""
    vm_id = get_vm_ids_dict()[name]
    print_info(f"Fixing characteristics on VM {name}...",
               command=f"malvm box fix {name}")
    subprocess.run(
        ["vagrant winrm -e -c malvm fix", vm_id], check=True,
    )


@box.command(name="list")
def list_boxes():
    """Prints all existing virtual machines."""
    vm_list = list(get_existing_vagrant_files_paths_iterable())
    if vm_list:
        print_info("List of virtual machines and vagrantfile path:",
                   command="malvm box list")
    else:
        print_info("No virtual machine setup yet.\n"
                   "Please create one with `malvm box run [template] [vm_name]`",
                   command="malvm box list")
    for vm_name, vagrantfile_path in vm_list:
        print_info(f"{vm_name} - {vagrantfile_path}")
