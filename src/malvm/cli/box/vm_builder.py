"""This module contains the CLI for creating sanitized windows Virtual Machines."""
import logging
import sys
from time import sleep

import click
import inquirer  # type: ignore
from malvm.controller.virtual_machine.hypervisor.virtualbox.virtualbox import create_snapshot

from ...characteristics.abstract_characteristic import Runtime
from ...controller import Controller
from ...utils.helper_methods import get_vm_malvm_package_file
from ..malvm.utils import print_pre_boot_fix_results
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
    vm_config = controller.vm_manager.get_vm_config(name)
    vm_config_network = controller.vm_manager.get_vm_config(name).network_configuration
    vm_config_network_interfaces = controller.vm_manager.get_vm_config(name).network_configuration.interfaces
    base_image = vm_config.base_image_name
    if not base_image and not controller.vm_manager.vm_exists(name):
        log.error(f"Virtual Machine {name} does not exist")
        print_warning(f"You can create the Virtual Machine {name} with:\n\n"
                      f"{click.style(f'> malvm box start {name} YOUR_BASE_IMAGE', fg='yellow')}")
        sys.exit(1)

    if base_image and not controller.vm_manager.vm_exists(vm_name=name):
        print_info(
            f"> Starting new [{click.style(base_image, fg='yellow')}] Virtual Machine "
            f"{click.style(name, fg='yellow')}..."
        )
        print_info(f"Settings:\n"
                   f"=========\n"
                   f"Name: {name}\n"
                   f"Base image: {base_image}\n"
                   f"Disk size: {vm_config.disk_size.strip().replace('GB', ' GB')}\n"
                   f"Memory: {vm_config.memory} MB\n"
                   f"Choco applications: {vm_config.choco_applications}\n"
                   f"Python applications: {vm_config.pip_applications}\n\n"
                   f"Network:\n"
                   f"=========\n"
                   f"Default Gateway: "
                   f"{vm_config_network.default_gateway if vm_config_network.default_gateway else 'Not set'}\n"
                   f"Interfaces:\n"
                   f"{vm_config_network_interfaces}\n\n"
                   )
        controller.vm_manager.build_vm(name, base_image)
        log.info("Wait 3 seconds..")
        sleep(3)
        # TODO Refactor: remove preboot logic from View
        if vm_config.hardening_configuration:
            vm_characteristic_list = vm_config.hardening_configuration.characteristics
            loaded_pre_boot_characteristics = [c.slug for c in
                                               controller.get_characteristic_list(include_sub_characteristics=True,
                                                                                  selected_runtime=Runtime.PRE_BOOT)]
            pre_boot_characteristic_list = filter(lambda c: c.upper() in loaded_pre_boot_characteristics,
                                                  vm_characteristic_list)
            print_pre_boot_fix_results(name, env={"pre_boot_characteristics": pre_boot_characteristic_list})
            log.info("Wait 3 seconds..")
            sleep(3)
            loaded_post_boot_characteristics = [c.slug for c in
                                                controller.get_characteristic_list(include_sub_characteristics=True)]
            post_boot_characteristic_list = filter(lambda c: c.upper() in loaded_post_boot_characteristics,
                                                   vm_characteristic_list)
            controller.vm_manager.initiate_first_boot(vm_name=name)
            controller.vm_manager.fix_vm(vm_name=name, characteristics=post_boot_characteristic_list)
        else:
            controller.vm_manager.initiate_first_boot(vm_name=name)
        create_snapshot(vm_name=name, snapshot_name="clean-state")
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
    print_info(f"Suspending VM {name}...", command=f"malvm box stop {name}")
    controller.vm_manager.stop_vm(name)


@box.command()
@click.argument("name")
def reset(name: str):
    """Resets Virtual Machine.

    Resetting by restoring the `clean-state` snapshot.
    """
    print_info(f"Resetting VM {name}...", command=f"malvm box reset {name}")
    controller.vm_manager.reset_vm(name)


@box.command()
@click.argument("name")
def destroy(name: str):
    """Destroys Virtual Machine and removes its data."""
    print_info(f"Destroying VM {name}...", command=f"malvm box destroy {name}")
    controller.vm_manager.destroy_vm(name)


@box.command()
@click.argument("vm_name")
@click.argument('characteristics', nargs=-1)
def fix(vm_name: str, characteristics):
    """Runs fixes on Virtual Machine."""
    print_info(f"Fixing characteristics on VM {vm_name}...", command=f"malvm box fix {vm_name}")
    loaded_inside_vm_characteristics = [c.slug for c in
                                        controller.get_characteristic_list(include_sub_characteristics=True)]
    if all([characteristic in loaded_inside_vm_characteristics for characteristic in
            characteristics]):
        controller.vm_manager.fix_vm(vm_name, list(characteristics))
    elif not characteristics:
        controller.vm_manager.fix_vm(vm_name, characteristics=None)
    print_pre_boot_fix_results(vm_name)


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
