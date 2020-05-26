"""This module contains the CLI for the malvm-tool."""

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
            slug, description, (_, return_values) = controller.run_check(
                characteristic.capitalize()
            )
        except ValueError as error_value:
            click.echo(click.style(str(error_value), fg="red"))
            exit(1)

        return_bool = return_values
        return_value_styled = return_bool_styled(return_values[-1] if)
        click.echo(
            f"[{click.style(slug, fg='yellow')}] {description} {return_value_styled}"
        )
    else:
        for slug, description, (_, return_values) in controller.run_checks():
            return_value_styled = return_bool_styled(return_values[-1])
            click.echo(
                f"[{click.style(slug, fg='yellow')}] {description} {return_value_styled}"
            )


@malvm.command()
@click.argument("characteristic", required=False)
def fix(characteristic: str) -> None:
    """Fixes satisfaction of CHARACTERISTIC."""
    characteristic_styled = (
        click.style(characteristic, fg="yellow")
        if characteristic
        else click.style("all", fg="yellow")
    )
    characteristic_sentence = (
        f"characteristic {characteristic_styled}"
        if characteristic
        else f"{characteristic_styled} characteristics"
    )
    click.echo(click.style("> Fixing ", fg="yellow") + characteristic_sentence)


@malvm.command()
def list() -> None:
    """Lists all characteristics."""
    controller: Controller = Controller()
    for characteristic in controller.get_characteristics():
        click.echo(
            f"[{click.style(characteristic.slug, fg='yellow')}] {characteristic.description}"
        )
