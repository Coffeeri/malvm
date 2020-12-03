"""This module contians cli for the malvm core."""
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

import click

from ..utils import print_error
from ...controller import Controller
from .utils import (
    get_vm_name,
    print_pre_boot_fix_results,
    print_characteristics,
    print_results,
)
from ...utils.helper_methods import (
    get_config_root,
    get_existing_vagrantfiles_paths_iterable,
    remove_path_with_success,
    get_vm_id_vagrantfile_path,
)

controller: Controller = Controller()


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
        vm_name = get_vm_name()
        if not vm_name:
            click.echo(
                click.style(
                    "No vm was found in your environment.\n"
                    "You can manually pass the vm-name with [-v VM_NAME].\n"
                    "If this was run in the VM, this can be ignored.",
                    fg="red",
                )
            )
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
        print_error(str(error_value))
        sys.exit(1)


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
        vm_name = get_vm_name()
        if not vm_name:
            click.echo(
                click.style(
                    "No vm was found in your environment.\n"
                    "You can manually pass the vm-name with [-v VM_NAME].\n"
                    "If this was run in the VM, this can be ignored.",
                    fg="red",
                )
            )
            sys.exit(0)
    print_pre_boot_fix_results(vm_name)


def run_specific_fix(characteristic_slug):
    try:
        print_results(controller.apply_fix_get_results(characteristic_slug.upper()))
    except ValueError as error_value:
        click.echo(click.style(str(error_value), fg="red"))


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
def clean(force: bool) -> None:
    """Removes all malvm data.

    This includes virtual machines and their Vagrantfiles, packer cache..
    This does not remove the malvm package itself.
    """
    clean_paths = [
        get_config_root(),
    ]
    vagrantfile_paths = get_existing_vagrantfiles_paths_iterable()
    if force:
        clean_malvm_data(clean_paths)
    else:
        click.echo("The following data will be deleted:")
        for path in clean_paths:
            click.echo(f"Path: {path.absolute()}")

        click.echo("The ENTIRE VM and its Vagrantfile will be destroyed:")
        for vm_name, vagrantfile in vagrantfile_paths:
            click.echo(f"{vm_name}: {vagrantfile}")

        user_conformation = input("Sure? This cannot be reversed. [y/n]").lower()
        if user_conformation == "y":
            clean_malvm_data(clean_paths)


def clean_malvm_data(clean_paths: List[Path]):
    destroy_virtual_machines()
    delete_malvm_data_paths(clean_paths)


def delete_malvm_data_paths(clean_paths: List[Path]):
    for path in clean_paths:
        remove_path_with_success(str(path.absolute()))


def destroy_virtual_machines():
    for vm_id, vagrantfile_path in get_vm_id_vagrantfile_path():
        destroy_virtual_machine(vm_id)
        remove_path_with_success(vagrantfile_path)


def destroy_virtual_machine(vm_id: str):
    subprocess.run(
        ["vagrant", "destroy", "--parallel", vm_id], check=True,
    )
