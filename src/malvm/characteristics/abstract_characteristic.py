"""This module contains an interface for characteristics.

A characteristic is an indication of the existence/ being inside
a virtual machine.

Classes:
    Characteristic: All characteristics classes will inherit from
                             this interface.
"""
import abc
import types
from typing import List, Tuple, Union, Dict, Any

CheckType = Union[Tuple[str, bool], List[Tuple[str, bool]]]


class Characteristic(metaclass=abc.ABCMeta):
    """Interface for all characteristics."""

    def __init__(self, slug: str = "", description: str = ""):
        self.__slug = slug
        self.__description = description
        self.__characteristics: Dict[str, types.FunctionType] = {}

    @property
    def characteristics(self) -> Dict[str, types.FunctionType]:
        """Returns all sub-characteristics.

        Returns:
            str: Unique slug referring to given characteristic.
        """
        return self.__characteristics

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

    @abc.abstractmethod
    def check(self) -> CheckType:
        """Checks if given characteristic is already satisfied."""

    @abc.abstractmethod
    def fix(self) -> CheckType:
        """Satisfies given characteristic."""


class LambdaCharacteristic(Characteristic):
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
