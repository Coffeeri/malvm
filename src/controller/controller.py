"""This module contains the controller for checks and fixes.

Classes:
    SingletonMeta: Singleton Metaclass.
    Controller: Controls the checks and fixes of characteristics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence, Dict, Type, Mapping, Any, Tuple, List

from ..characteristics.abstract_characteristic import Characteristic


class SingletonMeta(type):
    """Singleton Metaclass.

    All classes inheriting from SingletonMeta can be instantiated once.
    """

    _instances: Dict[SingletonMeta, Type[SingletonMeta]] = {}

    def __call__(
            cls, *args: Sequence[Any], **kwargs: Mapping[Any, Any]
    ) -> Type[SingletonMeta]:
        """Returns the instance of the class.

        Creates an instance of a class if it does not exist yet.

        Args:
            cls (SingletonMeta): Class which is defined by inheritance.
            *args (Sequence[Any]): Arguments for class.__call__.
            **kwargs (Mapping[Any, Any]): Keyword arguments for class.__call__.

        Returns:
            Type[SingletonMeta]: Instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Controller(metaclass=SingletonMeta):
    """The controller collects all characteristics.

    He stores codes, check-/ fix-methods.
    A task of a characteristic can register itself.
    """

    def __init__(self, characteristics_path="characteristics"):
        """Initialize Controller and load characteristics."""
        self.characteristics: Dict[str, Characteristic] = {}

        for path in Path(characteristics_path).glob("**/task.py"):
            pass  # TODO load modules dynamically.

    def register(self, characteristic: Characteristic) -> None:
        """Registers or updates a new characteristic."""
        self.characteristics[characteristic.code] = characteristic

    def unregister(self, characteristic_code: str) -> None:
        """Unregisters an existing characteristic."""
        if not isinstance(characteristic_code, str):
            raise TypeError("Characteristic Code is not of type `str`.")
        if characteristic_code not in self.characteristics:
            raise ValueError("Characteristic was not found.")

    def run_check(self, characteristic_code: str) -> Tuple[str, bool]:
        """Runs a check for a specified characteristic.

        Args:
            characteristic_code (str): A unique code representing a characteristic.
                                       Read more about it in the docs on Gitlab.

        Returns:
            Tuple[str, bool]:  Characteristic-Code + description and
                               its result.
        """
        if not isinstance(characteristic_code, str):
            raise TypeError("Characteristic Code is not of type `str`.")
        if characteristic_code not in self.characteristics:
            raise ValueError("Characteristic was not found.")
        characteristic = self.characteristics[characteristic_code]
        return (
            f"[{characteristic_code} {characteristic.description}]",
            characteristic.check(),
        )

    def run_checks(self) -> List[Tuple[str, bool]]:
        """Runs all checks and returns results.

        Returns:
            List[Tuple[str, bool]]: List of Characteristic-Code + description and
                                    its result.
        """
        results: List[Tuple[str, bool]] = []
        for characteristic_code, _ in self.characteristics.items():
            results.append(self.run_check(characteristic_code))
        return results
