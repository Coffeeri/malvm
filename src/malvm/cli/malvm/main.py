"""This module contians cli for the malvm core."""
import sys
from typing import Optional

import click

from ...controller import Controller
from .utils import print_result, get_vm_name

controller: Controller = Controller()


@click.command()
@click.argument("characteristic", required=False)
@click.option("-v", "--vm", "vm_name", type=str, default=False)
def check(characteristic: str, vm_name: Optional[str]) -> None:
    """Checks satisfaction of CHARACTERISTIC.

    [characteristic-code] for checking specific characteristic.
    All characteristics will be checked if not mentioned.
    """
    if characteristic:
        run_specific_check(characteristic)
    else:
        run_all_checks()

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


@click.command()
@click.argument("characteristic_slug", required=False)
@click.option("-v", "--vm", "vm_name", type=str, default=False)
def fix(characteristic_slug: str, vm_name: Optional[str]) -> None:
    """Fixes satisfaction of CHARACTERISTIC."""
    if characteristic_slug:
        try:
            for characteristic, status in controller.run_fix(
                characteristic_slug.upper()
            ):
                print_result(characteristic, status)
        except ValueError as error_value:
            click.echo(click.style(str(error_value), fg="red"))

    else:
        for characteristic, status in controller.run_fixes():
            print_result(characteristic, status)
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


def print_pre_boot_fix_results(vm_name: str):
    """Runs pre-boot fixes and prints the result to the screen."""
    for characteristic, status in controller.run_pre_boot_fixes({"vm_name": vm_name}):
        print_result(characteristic, status)


def print_pre_boot_check_results(vm_name: str):
    """Runs pre-boot fixes and prints the result to the screen."""
    for characteristic, status in controller.run_pre_boot_checks({"vm_name": vm_name}):
        print_result(characteristic, status)


@click.command()
@click.option("-a", "--show-all", "show_all", type=bool, is_flag=True, default=False)
def show(show_all: bool) -> None:
    """Lists all characteristics.

    Args:
        show_all: Returns a list of all characteristics, including sub characteristics.
    """
    characteristic_list = (
        controller.get_characteristic_list(True, None)
        if show_all
        else controller.get_characteristic_list(False, None)
    )
    for characteristic in characteristic_list:
        click.echo(
            f"[{click.style(characteristic.slug, fg='yellow')}] "
            f"{characteristic.description}"
        )


def run_all_checks() -> None:
    """Runs checks for all characteristics."""
    for characteristic, status in controller.run_checks():
        print_result(characteristic, status)


def run_specific_check(characteristic: str) -> None:
    """Runs checks of specific characteristic."""
    try:
        for check_return in controller.run_check(characteristic.upper()):
            print_result(*check_return)
    except ValueError as error_value:
        click.echo(click.style(str(error_value), fg="red"))
