"""This module contains the CLI for creating sanitized windows Virtual Machines."""
import logging
import sys
from time import sleep

import click
import inquirer  # type: ignore

from ..malvm.utils import print_pre_boot_fix_results
from ...controller import Controller
from ...utils.helper_methods import get_vm_malvm_package_file
from ..utils import print_info, print_warning

controller = Controller()
log = logging.getLogger()


@click.group(chain=True)
def box():
    """Handles Malboxes."""


@box.command()
@click.argument("template", type=click.Choice(["windows_10"]), required=False)
@click.argument("base_image_name", default="malvm-win-10")
def build(template: str, base_image_name: str):
    """Builds a Malbox template."""
    check_needed_files()
    log.warning("Currently only Windows 10 box implemented.")
    if not template:
        questions = [
            inquirer.List(
                "box-template",
                message="What Windows box template should be build?",
                choices=["windows_10"],
            ),
        ]
        template = inquirer.prompt(questions)["box-template"]
    click.clear()
    print_info(f"> Building template {click.style(template, fg='yellow')}...")
    box_config = controller.vm_manager.generate_box_config_by_base_image_name(base_image_name)
    controller.vm_manager.build_base_image(box_config)


def check_needed_files():
    if not get_vm_malvm_package_file().exists():
        log.error("Malvm.tar.gz was not found.\n"
                  "Please consider reinstalling with:\n"
                  "Run `malvm clean` and `source bootstrap.sh`")
        sys.exit(1)


@box.command()
@click.argument("name")
@click.argument(
    "base_image", required=False, type=click.Choice(controller.configuration.base_images.keys())
)
def start(name, base_image):
    """Run TEMPLATE as NAME in Virtualbox via Vagrant.

    TEMPLATE is the in `malvm box build` build template.
    NAME is the selected name of the VM spun up in VirtualBox.

    Examples:

        $ malvm box start win10-vm01 windows_10
    """
    if not base_image and not controller.vm_manager.vm_exists(name):
        log.error(f"Virtual Machine {name} does not exist")
        print_warning(f"You can create the Virtual Machine {name} with:\n\n"
                      f"{click.style(f'> malvm box start {name} YOUR_BASE_IMAGE', fg='yellow')}")
        sys.exit(1)
    if base_image:
        print_info(
            f"> Starting new [{click.style(base_image, fg='yellow')}] Virtual Machine "
            f"{click.style(name, fg='yellow')}..."
        )
        controller.vm_manager.build_vm(name, base_image)
        log.info("Wait 3 seconds..")
        sleep(3)
        # TODO If hardening == True in config
        print_pre_boot_fix_results(name)
        log.info("Wait 3 seconds..")
        sleep(3)
        controller.vm_manager.initiate_first_boot(name)
    else:
        print_info(f"Starting Virtual Machine {click.style(name, fg='yellow')}...")
        controller.vm_manager.start_vm(name)

    print_info(
        f"VM {name} was started. "
        f"A snapshot of the ´clean-state´ was saved.\n"
        f"Don't shutdown the VM, prefer to use these commands:\n\n"
        f"Stop VM:  `malvm box stop {name}`\n"
        f"Start VM: `malvm box start {name}`\n"
        f"Reset VM: `malvm box reset {name}`\n"
        f"Remove VM: `malvm box destroy {name}`\n\n"
        f"If you need to run `malvm fix` again in an elevated cmd, "
        f"please run on the host:\n"
        f"`malvm box fix {name}`\n"
        f"This will run the malvm in an shell with elevated privileges."
    )


@box.command()
@click.argument("name")
def stop(name: str):
    """Suspends Virtual Machine."""
    print_info(f"Suspending VM {name}...",
               command=f"malvm box stop {name}")
    controller.vm_manager.stop_vm(name)


@box.command()
@click.argument("name")
def reset(name: str):
    """Resets Virtual Machine.

    Resetting by restoring the `clean-state` snapshot.
    """
    print_info(f"Resetting VM {name}...",
               command=f"malvm box reset {name}")
    controller.vm_manager.reset_vm(name)


@box.command()
@click.argument("name")
def destroy(name: str):
    """Destroys Virtual Machine and removes its data."""
    print_info(f"Destroying VM {name}...",
               command=f"malvm box destroy {name}")
    controller.vm_manager.destroy_vm(name)


@box.command()
@click.argument("name")
def fix(name: str):
    """Runs fixes on Virtual Machine."""
    print_info(f"Fixing characteristics on VM {name}...",
               command=f"malvm box fix {name}")
    controller.vm_manager.fix_vm(name)


@box.command(name="list")
def list_boxes():
    """Prints all existing Virtual Machines."""
    vm_list = controller.vm_manager.get_virtual_machines_names_iter()
    if vm_list:
        print_info("List of Virtual Machines:",
                   command="malvm box list")
        for vm_name in vm_list:
            print_info(f"{vm_name}")
    else:
        print_info("No Virtual Machine setup yet.\n"
                   "Please create one with `malvm box start [template] [vm_name]`",
                   command="malvm box list")
