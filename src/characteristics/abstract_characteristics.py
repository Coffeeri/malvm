"""This module contains an interface for characteristics.

A characteristic is an indication of the existence/ being inside
a virtual machine.

Classes:
    AbstractCharacteristics: All characteristics classes will inherit from
                             this interface.
"""
import abc


class AbstractCharacteristics(metaclass=abc.ABCMeta):
    """Interface for all characteristics."""

    def check(self) -> bool:
        """Checks if given characteristic is already satisfied."""

    def fix(self) -> None:
        """Satisfies given characteristic."""
