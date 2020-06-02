"""This module contains an interface for characteristics.

A characteristic is an indication of the existence/ being inside
a virtual machine.

Classes:
    CharacteristicBase: Baseclass with data for inheriting classes, such as
                        Characteristic class oder LambdaCharacteristic
    Characteristic: All characteristics classes will inherit from
                             this interface.
    LambdaCharacteristic: Sub-characteristic with flexible function pointers as check
                          and fix methods.
"""
from __future__ import annotations

import abc
import types
from typing import Any, Dict, Generator, List, Optional, NamedTuple


class CheckType(NamedTuple):
    """Return-Type for check and fix functions."""

    slug: str
    description: str
    check_value: str
    check_status: bool


GeneratorCheckType = Generator[CheckType, None, None]


class CharacteristicBase:
    """Base class for Characteristic class or any sub-characteristic class."""

    def __init__(self, slug: str = "", description: str = ""):
        if not slug.isupper():
            raise ValueError("Slug of characteristic must be uppercase.")
        self.__slug = slug
        self.__description = description
        self.__sub_characteristics: Dict[str, CharacteristicBase] = {}

    @abc.abstractmethod
    def check(self) -> Any:
        """Checks if given characteristic is already satisfied."""

    @abc.abstractmethod
    def fix(self) -> Any:
        """Satisfies given characteristic."""

    @property
    def slug(self) -> str:
        """Unique slug referring to given characteristic.

        Returns:
            str: Unique slug referring to given characteristic.
        """
        return self.__slug

    @slug.setter
    def slug(self, slug: str) -> None:
        """Sets unique slug referring to given characteristic.

        Args:
            slug (str): Unique slug referring to given characteristic.
        """
        # add some checks for "slug"-style
        self.__slug = slug

    @property
    def description(self) -> str:
        """Description or content of characteristic.

        Giving some context to the given characteristic.
        """
        return self.__description

    @description.setter
    def description(self, description: str) -> None:
        """Setter for description method.

        Args:
            description (str): Description or content for context of
                               characteristic.
        """
        # add some checks for "description"-style
        self.__description = description

    @property
    def sub_characteristics(self) -> Dict[str, CharacteristicBase]:
        """Returns a sub-characteristics.

        Returns:
            Dict[str, CharacteristicBase]: A dict of a sub-characteristics.
        """
        return self.__sub_characteristics

    def add_sub_characteristic(self, sub_characteristic: CharacteristicBase) -> None:
        """Add a sub-characteristic.

        Args:
            sub_characteristic (CharacteristicBase): Sub characteristic which will be
                                                     added.
        """
        self.__sub_characteristics[sub_characteristic.slug] = sub_characteristic

    def add_sub_characteristic_list(
        self, sub_characteristic_list: List[CharacteristicBase]
    ) -> None:
        """Add a list of sub-characteristics.

        Args:
            sub_characteristic_list (List[CharacteristicBase]): Sub characteristics
                                        which will be added.
        """
        for characteristic in sub_characteristic_list:
            self.add_sub_characteristic(characteristic)

    def find(self, slug: str) -> Optional[CharacteristicBase]:
        """Finds and returns a characteristic by slug.

        Args:
            slug(str): A unique slug, which is associated with the characteristic.

        Returns:
            Optional[CharacteristicBase]: A characteristic object.
        """
        if slug in self.sub_characteristics:
            return self.sub_characteristics[slug]

        for characteristic in self.sub_characteristics.values():
            check_result: Optional[CharacteristicBase] = characteristic.find(slug)
            if check_result:
                return check_result
        return None


class Characteristic(CharacteristicBase, metaclass=abc.ABCMeta):
    """Interface for a characteristics."""

    def __init__(self, slug: str = "", description: str = ""):
        super().__init__(slug, description)
        self.__slug = slug
        self.__description = description

    def check(self) -> GeneratorCheckType:
        """Checks if given characteristic is already satisfied."""
        no_errors = True
        result_list: List[CheckType] = []
        if self.sub_characteristics:
            for sub_characteristic in self.sub_characteristics.values():
                result = sub_characteristic.check()
                if not result[-1]:
                    no_errors = False
                result_list.append(result)
        yield CheckType(self.slug, self.description, "Summary", no_errors)
        for result in result_list:
            result = list(result)
            result[0] = "|-- " + result[0]
            result = tuple(result)
            yield result

    def fix(self) -> GeneratorCheckType:
        """Satisfies given characteristic."""
        no_errors = True
        result_list: List[CheckType] = []
        if self.sub_characteristics:
            for sub_characteristic in self.sub_characteristics.values():
                result = sub_characteristic.fix()
                if not result[-1]:
                    no_errors = False
                result_list.append(result)
        yield CheckType(self.slug, self.description, "Summary", no_errors)
        for result in result_list:
            result = list(result)
            result[0] = "|-- " + result[0]
            result = tuple(result)
            yield result


class LambdaCharacteristic(CharacteristicBase):
    """A LambdaCharacteristic is used as a sub-characteristic.

    LambdaCharacteristics live from function pointers.
    """

    def __init__(
        self,
        slug: str,
        description: str,
        value: Any,
        check_func: types.FunctionType,
        fix_func: types.FunctionType,
    ):
        """Initializes function pointers of LambdaCharacteristic."""
        super().__init__(slug, description)
        self.__check = check_func
        self.__fix = fix_func
        self.__value = value

    def check(self) -> CheckType:
        """Checks if given characteristic is already satisfied."""
        return self.__check(self.__value)

    def fix(self) -> CheckType:
        """Satisfies given characteristic."""
        self.__fix(self.__value)
        return self.check()
