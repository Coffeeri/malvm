"""This module contians cli for the malvm core."""
import sys

import click

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
@click.argument("characteristic", required=False)
def fix(characteristic: str) -> None:
    """Fixes satisfaction of CHARACTERISTIC."""
    if characteristic:
        try:
            for slug, description, _, status in controller.run_fix(
                characteristic.upper()
            ):
                print_result(slug, status, description)
        except ValueError as error_value:
            click.echo(click.style(str(error_value), fg="red"))
            sys.exit(1)

    else:
        for slug, description, _, status in controller.run_fixes():
            print_result(slug, status, description)


@click.command()
@click.option("-a", "--show-all", "show_all", type=bool, is_flag=True, default=False)
def show(show_all: bool) -> None:
    """Lists all characteristics.

    Args:
        show_all: Returns a list of all characteristics, including sub characteristics.
    """
    characteristic_list = (
        controller.get_characteristic_list_all()
        if show_all
        else controller.get_characteristic_list()
    )
    for characteristic in characteristic_list:
        click.echo(
            f"[{click.style(characteristic.slug, fg='yellow')}] "
            f"{characteristic.description}"
        )


def run_all_checks() -> None:
    """Runs checks for all characteristics."""
    for slug, description, _, status in controller.run_checks():
        print_result(slug, status, description)


def print_result(slug: str, status: bool, description: str):
    """Prints formatted result via Click."""
    return_value_styled = return_bool_styled(status)
    click.echo(
        f"[{click.style(slug, fg='yellow')}]  {return_value_styled} - {description}"
    )


def run_specific_check(characteristic: str) -> None:
    """Runs checks of specific characteristic."""
    try:
        for slug, _, value, status in controller.run_check(characteristic.upper()):
            print_result(slug, status, value)
    except ValueError as error_value:
        click.echo(click.style(str(error_value), fg="red"))
        sys.exit(1)
