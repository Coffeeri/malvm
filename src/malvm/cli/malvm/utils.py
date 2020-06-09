"""This module contains helper methods for cli malvm-core."""
import click


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
