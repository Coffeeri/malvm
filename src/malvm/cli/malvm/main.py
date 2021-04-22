"""This module contians cli for the malvm core."""
import logging
import sys
from typing import Optional

import click

from ..utils import print_info
from ...controller import Controller
from .utils import (print_pre_boot_fix_results,
                    print_characteristics,
                    print_results,
                    )
from ...controller.virtual_machine.hypervisor.virtualbox.vagrant import get_existing_vagrant_files_paths_iterable

controller: Controller = Controller()
log = logging.getLogger()


@click.command()
@click.argument(
    "characteristic", required=False,
)
@click.option("-v", "--vm", "vm_name", type=str, default=False)
def check(characteristic: Optional[str], vm_name: Optional[str]) -> None:
    """Checks satisfaction of CHARACTERISTIC.

    All characteristics will be checked if non is specified.
    """
    if characteristic:
        run_specific_check(characteristic)
    else:
        run_all_checks()

    # Müssen wir Auge machen.
    if not vm_name:
        log.warning("No vm was found in your environment.\n"
                    "You can manually pass the vm-name with [-v VM_NAME].\n"
                    "If this ran in the VM, this can be ignored.")
        sys.exit(0)
    print_pre_boot_fix_results(vm_name)


def run_all_checks() -> None:
    """Runs checks for all characteristics."""
    print_results(controller.get_all_checks_results())


def run_specific_check(characteristic: str) -> None:
    """Runs checks of specific characteristic."""
    try:
        print_results(controller.get_check_results(characteristic.upper()))
    except ValueError as error_value:
        log.exception(error_value)


@click.command()
@click.argument("characteristic_slug", required=False)
@click.option("-v", "--vm", "vm_name", type=str, default=False)
def fix(characteristic_slug: str, vm_name: Optional[str]) -> None:
    """Fixes satisfaction of CHARACTERISTIC."""
    if characteristic_slug:
        run_specific_fix(characteristic_slug)

    else:
        run_all_fixes()

    # Müssen wir Auge machen.
    if not vm_name:
        log.warning("No vm was found in your environment.\n"
                    "You can manually pass the vm-name with [-v VM_NAME].\n"
                    "If this ran in the VM, this can be ignored.")
        sys.exit(0)
    print_pre_boot_fix_results(vm_name)


def run_specific_fix(characteristic_slug):
    try:
        print_results(controller.apply_fix_get_results(characteristic_slug.upper()))
    except ValueError as error_value:
        log.exception(error_value)


def run_all_fixes():
    print_results(controller.apply_all_fixes_get_results())


@click.command()
@click.option("-a", "--show-all", "show_all", type=bool, is_flag=True, default=False)
def show(show_all: bool) -> None:
    """Prints list of characteristics.

    Args:
        show_all: Includes sub characteristics.
    """
    characteristic_list = (
        controller.get_characteristic_list(True, None)
        if show_all
        else controller.get_characteristic_list(False, None)
    )
    print_characteristics(characteristic_list)


@click.command()
@click.option("-f", "--force", type=bool, is_flag=True, default=False)
@click.option("-s", "--soft", type=bool, is_flag=True, default=False)
def clean(force: bool, soft: bool) -> None:
    """Removes all malvm data.

    This includes Virtual Machines and their Vagrantfiles, packer cache..
    This does not remove the malvm package itself.
    """

    vagrantfile_paths = get_existing_vagrant_files_paths_iterable()
    if force:
        controller.clean_malvm_data(soft)
    else:
        if not soft:
            print_info("The following data will be deleted:",
                       command=f"malvm clean {'-f' if force else ''}")
            for path in controller.dirty_paths:
                print_info(f"Path: {path.absolute()}", command="clean()")

        print_info("VMs and Vagrantfiles will be destroyed and removed:")
        for vm_name, vagrantfile in vagrantfile_paths:
            print_info(f"{vm_name}: {vagrantfile}")

        user_conformation = input("Sure? This cannot be reversed. [y/n]").lower()
        if user_conformation == "y":
            controller.clean_malvm_data(soft)


@click.command()
def up():  # pylint: disable=invalid-name
    """Creates base images and Virtual Machines from configuration file."""
    controller.vm_manager.build_base_images_in_config()
    controller.vm_manager.build_vms_in_config()
