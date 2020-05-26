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
from typing import List, Tuple, Any, Generator

CheckType = Tuple[str, bool]
GeneratorCheckType = Generator[CheckType, None, None]


class CharacteristicBase:
    """Base class for Characteristic class or any sub-characteristic class."""

    def __init__(self, slug: str = "", description: str = ""):
        self.__slug = slug
        self.__description = description

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


class Characteristic(CharacteristicBase, metaclass=abc.ABCMeta):
    """Interface for all characteristics."""

    def __init__(self, slug: str = "", description: str = ""):
        super().__init__(slug, description)
        self.__slug = slug
        self.__description = description
        self.__sub_characteristics: List[CharacteristicBase] = []

    @property
    def sub_characteristics(self) -> List[CharacteristicBase]:
        """Returns all sub-characteristics.

        Returns:
            str: Unique slug referring to given characteristic.
        """
        return self.__sub_characteristics

    def check(self) -> GeneratorCheckType:
        """Checks if given characteristic is already satisfied."""
        if self.sub_characteristics:
            for sub_characteristic in self.sub_characteristics:
                yield sub_characteristic.check()

    def fix(self) -> GeneratorCheckType:
        """Satisfies given characteristic."""
        if self.sub_characteristics:
            for sub_characteristic in self.sub_characteristics:
                yield sub_characteristic.fix()


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
        super().__init__()
        self.__check = check_func
        self.__fix = fix_func
        self.__value = value

    def check(self) -> CheckType:
        """Checks if given characteristic is already satisfied."""
        return self.__check(self.__value)

    def fix(self) -> CheckType:
        """Satisfies given characteristic."""
        self.__fix()
        return self.check()
