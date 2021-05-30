"""This module contains helper methods for cli malvm-core."""
import platform
from typing import Iterator, List, Tuple, Dict

import click

from ...characteristics.abstract_characteristic import (CharacteristicBase,
                                                        CheckType)
from ...controller import Controller
from ..utils import print_info

controller: Controller = Controller()


def return_bool_styled(return_value: bool) -> str:
    """Returns a styled version of check return values."""
    return_value_styled = (
        click.style("OK.", fg="green")
        if return_value
        else click.style("NEEDS FIX.", fg="red")
    )
    return return_value_styled


def print_results(results: Iterator[Tuple[CharacteristicBase, CheckType]]):
    for result in results:
        print_result(*result)


def print_result(characteristic: CharacteristicBase, status: CheckType):
    """Prints formatted result."""

    return_value_styled = return_bool_styled(status.check_status)
    print_info(
        f"[{click.style(characteristic.slug, fg='yellow')}] - {return_value_styled} "
        f"- {click.style(status.check_value, fg='green')}"
    )


def print_pre_boot_fix_results(vm_name: str, env: Dict = None):
    environment = {"os": platform.system(), "vm_name": vm_name}
    if env:
        environment = {**environment, **env}
    # for characteristic, return_status in controller.apply_pre_boot_fixes(environment):
    #   print_result(characteristic, return_status)
    print_results(controller.apply_pre_boot_fixes(environment))


def print_pre_boot_check_results(vm_name: str):
    print_results(controller.get_pre_boot_checks_results({"vm_name": vm_name}))


def print_characteristics(characteristic_list: List[CharacteristicBase]):
    for characteristic in characteristic_list:
        print_info(
            f"[{click.style(characteristic.slug, fg='yellow')}] "
            f"{characteristic.description}", command="print_characteristics()")
