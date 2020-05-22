"""This module contains an interface for characteristics.

A characteristic is an indication of the existence/ being inside
a virtual machine.

Classes:
    Characteristic: All characteristics classes will inherit from
                             this interface.
"""
import abc


class Characteristic(metaclass=abc.ABCMeta):
    """Interface for all characteristics."""

    def __init__(self):
        self.__code = ""
        self.__description = ""

    @property
    def code(self) -> str:
        """Unique code referring to given characteristic.

        Returns:
            str: Unique code referring to given characteristic.
        """
        return self.__code

    @code.setter
    def code(self, code: str) -> None:
        """Sets unique code referring to given characteristic.

        Args:
            code (str): Unique code referring to given characteristic.
        """
        # add some checks for "code"-style
        self.__code = code

    @property
    def description(self) -> str:
        """Description or content of characteristic.

        Giving some context to the given characteristic.
        """
        return self.description

    @description.setter
    def description(self, description: str) -> None:
        """Setter for description method.

        Args:
            description (str): Description or content for context of
                               characteristic.
        """
        # add some checks for "description"-style
        self.description = description

    def check(self) -> bool:
        """Checks if given characteristic is already satisfied."""

    def fix(self) -> None:
        """Satisfies given characteristic."""
