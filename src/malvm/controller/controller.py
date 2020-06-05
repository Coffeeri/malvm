"""This module contains the controller for checks and fixes.

Classes:
    SingletonMeta: Singleton Metaclass.
    Controller: Controls the checks and fixes of characteristics.
"""
from typing import Dict, Generator, List, Optional

from ..characteristics import loaded_characteristics
from ..characteristics.abstract_characteristic import CharacteristicBase, CheckType
from ..utils.metaclasses import SingletonMeta


class Controller(metaclass=SingletonMeta):
    """The controller collects all characteristics.

    The Controller also runs, check-/ fix-methods.
    """

    def __init__(self) -> None:
        """Initialize Controller and load characteristics."""
        self.characteristics: Dict[str, CharacteristicBase] = {}
        for characteristic in loaded_characteristics:
            sub_characteristics = {
                c.slug: c for c in characteristic().sub_characteristics.values()
            }
            self.characteristics = {
                **self.characteristics,
                characteristic().slug: characteristic(),
            }
            self.characteristics_with_sub_characteristics = {
                **self.characteristics,
                characteristic().slug: characteristic(),
                **sub_characteristics,
            }

    def get_characteristic_list(self) -> List[CharacteristicBase]:
        """Returns all characteristics.

        Returns:
            List[CharacteristicBase]: List of all characteristics.
        """

        return list(self.characteristics.values())

    def get_characteristic_list_all(self) -> List[CharacteristicBase]:
        """Returns all characteristics, including sub-characteristics.

        Returns:
            List[CharacteristicBase]: List of all characteristics,
                                      including all sub-characteristics.
        """

        return list(self.characteristics_with_sub_characteristics.values())

    def run_check(self, slug_searched: str) -> Generator[CheckType, None, None]:
        """Runs a check for a specified characteristic.

        Args:
            slug_searched (str): A unique slug representing a characteristic.
                                       Read more about it in the docs on Gitlab.

        Returns:
            RunCheckType:  Characteristic-Code, description and result of check.
        """
        if not isinstance(slug_searched, str):
            raise TypeError("Characteristic Code is not of type `str`.")
        if slug_searched not in self.characteristics:
            raise ValueError("Characteristic was not found.")
        characteristic = self.characteristics[slug_searched]
        characteristic_return_value = characteristic.check()
        if not isinstance(  # pylint: disable=isinstance-second-argument-not-valid-type
            characteristic_return_value, Generator,
        ):
            yield characteristic_return_value
        else:
            for result in characteristic.check():
                yield result

    def run_checks(self) -> Generator[CheckType, None, None]:
        """Runs all checks and returns their results.

        Returns:
            Generator[RunCheckType]: Generator of Characteristic-Code, description
                                     and result of check.
        """
        for characteristic_slug in self.characteristics.keys():
            for result in self.run_check(characteristic_slug):
                yield result

    def run_fix(self, slug_searched: str) -> Generator[CheckType, None, None]:
        """Runs a fix for a specified characteristic.

        Args:
            slug_searched (str): A unique slug representing a characteristic.
                                       Read more about it in the docs on Gitlab.

        Returns:
            RunCheckType:  Characteristic-Code, description and result of fix.
                               The result consists of Tuple of a message and a bool,
                               which indicates the status.
        """
        if not isinstance(slug_searched, str):
            raise TypeError("Characteristic Code is not of type `str`.")
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

    def run_fixes(self) -> Generator[CheckType, None, None]:
        """Runs fixes for all characteristics and returns their success.

        Returns:
            List[RunCheckType]: List of Characteristic-Code, description
                                and result of fix.
                                The result consists of Tuple of a message and a bool,
                                which indicates the success.
        """
        for characteristic_slug in self.characteristics.keys():
            for characteristics in self.run_fix(characteristic_slug):
                yield characteristics

    def find(self, slug: str) -> Optional[CharacteristicBase]:
        """Finds and returns a characteristic by slug.

        Args:
            slug(str): A unique slug, which is associated with the characteristic.

        Returns:
            Optional[CharacteristicBase]: A characteristic object.
        """
        if slug in self.characteristics:
            return self.characteristics[slug]

        for characteristic in self.characteristics.values():
            check_result: Optional[CharacteristicBase] = characteristic.find(slug)
            if check_result:
                return check_result
        return None