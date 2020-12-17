"""This module contains helper methods for cli malvm-core."""
import re
from pathlib import Path
from typing import Optional, List, Iterator, Tuple

import click
from malvm.utils.logging import logger

from ..utils import print_info
from ...characteristics.abstract_characteristic import CharacteristicBase, CheckType
from ...controller import Controller

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


def get_vm_name() -> Optional[str]:
    """Returns vm-name related to Vagrantfile in current path."""
    path = Path.cwd() / "Vagrantfile"
    if path.exists():

        text_file = open(str(path.absolute()), "r")
        text_file_content = text_file.read()
        text_file.close()
        matches = re.findall(r"vb\.name = \"(\S+)\"", text_file_content)
        if matches:
            return matches[0]
    return None


def print_pre_boot_fix_results(vm_name: str):
    print_results(controller.apply_pre_boot_fixes({"vm_name": vm_name}))


def print_pre_boot_check_results(vm_name: str):
    print_results(controller.get_pre_boot_checks_results({"vm_name": vm_name}))


def print_characteristics(characteristic_list: List[CharacteristicBase]):
    for characteristic in characteristic_list:
        logger.info("Command: Listing characteristics:")
        print_info(
            f"[{click.style(characteristic.slug, fg='yellow')}] "
            f"{characteristic.description}"
        )
