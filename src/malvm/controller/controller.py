"""This module contains the controller for checks and fixes.

Classes:
    SingletonMeta: Singleton Metaclass.
    Controller: Controls the checks and fixes of characteristics.
"""
from typing import Any, Dict, Generator, List, Optional

from ..characteristics import loaded_characteristics
from ..characteristics.abstract_characteristic import (
    CharacteristicBase,
    GeneratorCheckType,
    Runtime,
)
from ..utils.metaclasses import SingletonMeta


class Controller(metaclass=SingletonMeta):
    """The controller collects all characteristics.

    The Controller also runs, check-/ fix-methods.
    """

    def __init__(self) -> None:
        """Initialize Controller and load characteristics."""
        self.characteristics: Dict[str, CharacteristicBase] = {}
        self.characteristics_with_sub_characteristics: Dict[
            str, CharacteristicBase
        ] = {}
        for characteristic in loaded_characteristics:
            sub_characteristics = {
                c.slug: c for c in characteristic().sub_characteristics.values()
            }
            self.characteristics = {
                **self.characteristics,
                characteristic().slug: characteristic(),
            }
            self.characteristics_with_sub_characteristics = {
                **self.characteristics_with_sub_characteristics,
                characteristic().slug: characteristic(),
                **sub_characteristics,
            }

    def get_characteristic_list(
        self,
        include_sub_characteristics: bool = False,
        runtime: Optional[Runtime] = Runtime.DEFAULT,
    ) -> List[CharacteristicBase]:
        """Returns all characteristics.

        Args:
            include_sub_characteristics (bool): Select True if sub characteristics
                                                should be included.
            runtime (Runtime): Enum, defining the time and location when check and fix
                               methods will be executed.
        """
        if include_sub_characteristics:
            characteristics = self.characteristics_with_sub_characteristics
        else:
            characteristics = self.characteristics
        return list(
            characteristic
            for characteristic in characteristics.values()
            if ((characteristic.attributes.runtime == runtime) or (runtime is None))
        )

    def run_check(self, slug_searched: str) -> GeneratorCheckType:
        """Runs a check for a specified characteristic.

        Args:
            slug_searched (str): A unique slug representing a characteristic.
                                       Read more about it in the docs on Gitlab.

        Returns:
            GeneratorCheckType: Generator of characteristic and result of check.
        """
        if slug_searched not in self.characteristics_with_sub_characteristics:
            raise ValueError("Characteristic was not found.")
        characteristic = self.characteristics_with_sub_characteristics[slug_searched]
        characteristic_return_value = characteristic.check()
        if not isinstance(  # pylint: disable=isinstance-second-argument-not-valid-type
            characteristic_return_value, Generator,
        ):
            yield characteristic_return_value
        else:
            for result in characteristic.check():
                yield result

    def run_checks(self) -> GeneratorCheckType:
        """Runs all checks and returns their results.

        Returns:
            GeneratorCheckType: Generator of characteristic and result of check.
        """
        for characteristic_slug in self.characteristics.keys():
            for result in self.run_check(characteristic_slug):
                yield result

    def run_fix(self, slug_searched: str) -> GeneratorCheckType:
        """Runs a fix for a specified characteristic.

        Args:
            slug_searched (str): A unique slug representing a characteristic.
                                       Read more about it in the docs on Gitlab.

        Returns:
            GeneratorCheckType: Characteristic and result of fix.
        """
        if not isinstance(slug_searched, str):
            raise TypeError("Characteristic Slug is not of type `str`.")
        if slug_searched not in self.characteristics:
            raise ValueError("Characteristic was not found.")
        characteristic = self.characteristics[slug_searched]
        characteristic_return_value = characteristic.fix()
        if not isinstance(  # pylint: disable=isinstance-second-argument-not-valid-type
            characteristic_return_value, Generator,
        ):
            yield characteristic_return_value
        else:
            for result in characteristic.fix():
                yield result

    def run_fixes(self) -> GeneratorCheckType:
        """Runs fixes for all characteristics and returns their success.

        Returns:
            GeneratorCheckType: List of Characteristic and result of fix.
        """
        for characteristic_slug in self.characteristics.keys():
            for fix_return_value in self.run_fix(characteristic_slug):
                yield fix_return_value

    def run_pre_boot_fixes(self, environment: Dict[str, Any]) -> GeneratorCheckType:
        """Runs fixes for all pre boot characteristics and returns their success.

        Returns:
            GeneratorCheckType: List of Characteristic and result of fix.
        """
        for characteristic in self.get_characteristic_list(True, Runtime.PRE_BOOT):
            self.characteristics[characteristic.slug].environment = environment
            yield from self.run_fix(characteristic.slug)
