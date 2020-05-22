"""This module contains an interface for characteristics.

A characteristic is an indication of the existence/ being inside
a virtual machine.

Classes:
    AbstractCharacteristics: All characteristics classes will inherit from
                             this interface.
"""
import abc
from typing import Tuple, List


class AbstractCharacteristics(metaclass=abc.ABCMeta):
    """Interface for all characteristics."""

    @abc.abstractmethod
    def check(self) -> List[Tuple[str, bool]]:
        """Checks if given characteristic is already satisfied."""

    @abc.abstractmethod
    def fix(self) -> None:
        """Satisfies given characteristic."""
