"""This module contains the CLI for the malvm-tool."""
import click


@click.group()
def malvm():
    """Base CLI-command for malvm."""


@malvm.command()
@click.argument("characteristic", required=False)
def check(characteristic: str) -> None:
    """Checks satisfaction of CHARACTERISTIC."""
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
    click.echo(click.style("> Checking ", fg="yellow") + characteristic_sentence)


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


if __name__ == "__main__":
    malvm()
