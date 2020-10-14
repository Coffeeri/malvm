"""This module contains helper methods for cli malvm-core."""
import re
from pathlib import Path
from typing import Optional

import click

from malvm.characteristics.abstract_characteristic import CharacteristicBase, CheckType


def return_bool_styled(return_value: bool) -> str:
    """Returns a styled version of check return values.

    Returns:
        str: Click-styled value.
    """
    return_value_styled = (
        click.style("OK.", fg="green")
        if return_value
        else click.style("NEEDS FIX.", fg="red")
    )
    return return_value_styled


def print_result(characteristic: CharacteristicBase, status: CheckType):
    """Prints formatted result via Click."""

    return_value_styled = return_bool_styled(status.check_status)
    click.echo(
        f"[{click.style(characteristic.slug, fg='yellow')}] - {return_value_styled} "
        f"- {click.style(status.check_value, fg='green')}"
    )


def get_vm_name() -> Optional[str]:
    """Returns vm-name of Vagrantfile in current path.

    Returns:
        str: Returns vm-name of Vagrantfile. None if no Vagrantfile was found.
    """
    path = Path.cwd() / "Vagrantfile"
    if path.exists():

        textfile = open(str(path.absolute()), "r")
        filetext = textfile.read()
        textfile.close()
        matches = re.findall(r"vb\.name = \"(\S+)\"", filetext)
        if matches:
            return matches[0]
    return None
