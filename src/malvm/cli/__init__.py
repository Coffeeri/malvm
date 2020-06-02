"""This module contains the CLI for the malvm-tool."""
import sys

import click

from ..controller.controller import Controller


@click.group()
def malvm():
    """Base CLI-command for malvm."""


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


@malvm.command()
@click.argument("characteristic", required=False)
def check(characteristic: str) -> None:
    """Checks satisfaction of CHARACTERISTIC.

    [characteristic-code] for checking specific characteristic.
    All characteristics will be checked if not mentioned.
    """
    controller: Controller = Controller()
    if characteristic:
        try:
            for slug, description, value, status in controller.run_check(
                characteristic.upper()
            ):
                return_value_styled = return_bool_styled(status)
                click.echo(
                    f"[{click.style(slug, fg='yellow')}] "
                    f"{description} {value} "
                    f"{return_value_styled}"
                )
        except ValueError as error_value:
            click.echo(click.style(str(error_value), fg="red"))
            sys.exit(1)

    else:
        for slug, description, value, status in controller.run_checks():
            return_value_styled = return_bool_styled(status)
            click.echo(
                f"[{click.style(slug, fg='yellow')}] "
                f"{description} "
                f"{return_value_styled}"
            )


@malvm.command()
@click.argument("characteristic", required=False)
def fix(characteristic: str) -> None:
    """Fixes satisfaction of CHARACTERISTIC."""
    controller: Controller = Controller()
    if characteristic:
        try:
            for slug, description, value, status in controller.run_fix(
                characteristic.upper()
            ):
                return_value_styled = return_bool_styled(status)
                click.echo(
                    f"[{click.style(slug, fg='yellow')}] "
                    f"{description} {value} "
                    f"{return_value_styled}"
                )
        except ValueError as error_value:
            click.echo(click.style(str(error_value), fg="red"))
            sys.exit(1)

    else:
        for slug, description, value, status in controller.run_fixes():
            return_value_styled = return_bool_styled(status)
            click.echo(
                f"[{click.style(slug, fg='yellow')}] "
                f"{description} "
                f"{return_value_styled}"
            )


@malvm.command()
@click.option("-a", "--show-all", "show_all", type=bool, is_flag=True, default=False)
def show(show_all: bool) -> None:
    """Lists all characteristics.

    Args:
        show_all: Returns a list of all characteristics, including sub characteristics.
    """
    controller: Controller = Controller()
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
