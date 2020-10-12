"""This module contians cli for the malvm core."""
import sys

import click

from ...characteristics.abstract_characteristic import CharacteristicBase, CheckType
from ...controller import Controller
from .utils import return_bool_styled

controller: Controller = Controller()


@click.command()
@click.argument("characteristic", required=False)
def check(characteristic: str) -> None:
    """Checks satisfaction of CHARACTERISTIC.

    [characteristic-code] for checking specific characteristic.
    All characteristics will be checked if not mentioned.
    """
    if characteristic:
        run_specific_check(characteristic)
    else:
        run_all_checks()


@click.command()
@click.argument("characteristic_slug", required=False)
def fix(characteristic_slug: str) -> None:
    """Fixes satisfaction of CHARACTERISTIC."""
    if characteristic_slug:
        try:
            for characteristic, status in controller.run_fix(
                characteristic_slug.upper()
            ):
                print_result(characteristic, status)
        except ValueError as error_value:
            click.echo(click.style(str(error_value), fg="red"))
            sys.exit(1)

    else:
        for characteristic, status in controller.run_fixes():
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


def print_result(characteristic: CharacteristicBase, status: CheckType):
    """Prints formatted result via Click."""

    return_value_styled = return_bool_styled(status.check_status)
    click.echo(
        f"[{click.style(characteristic.slug, fg='yellow')}] - {return_value_styled} "
        f"- {click.style(status.check_value, fg='green')}"
    )


def run_specific_check(characteristic: str) -> None:
    """Runs checks of specific characteristic."""
    try:
        for check_return in controller.run_check(characteristic.upper()):
            print_result(*check_return)
    except ValueError as error_value:
        click.echo(click.style(str(error_value), fg="red"))
        sys.exit(1)
