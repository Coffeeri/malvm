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

import abc
import platform
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, NamedTuple, Tuple


class CheckType(NamedTuple):
    """Return-Type for check and fix functions."""

    check_value: str
    check_status: bool


class Runtime(Enum):
    """Enum defining the execution-time of a characteristic."""

    DEFAULT = 1
    PRE_BOOT = 2

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value  # pylint: disable=comparison-with-callable
        return NotImplemented


class CharacteristicAttributes(NamedTuple):
    """Attributes of a characteristic."""

    runtime: Runtime


class VMType(NamedTuple):
    """Attributes of a virtual machine."""

    name: str


def get_current_runtime() -> Runtime:
    """Returns the current os, in which malvm is executed."""
    if platform.system() == "Windows":
        return Runtime.DEFAULT
    return Runtime.PRE_BOOT


class CharacteristicBase:
    """Base class for Characteristic class or any sub-characteristic class."""

    def __init__(
        self, slug: str, description: str, attributes: CharacteristicAttributes,
    ):
        if not slug.isupper():
            raise ValueError("Slug of characteristic must be uppercase.")
        self.__slug = slug
        self.__description = description
        self.__sub_characteristics: Dict[str, CharacteristicBase] = {}
        self.__attributes: CharacteristicAttributes = attributes
        self.__environment: Dict[str, Any] = {}

    def __eq__(self, other: Any) -> bool:
        """Returns true if compared characteristic is equal."""
        if not isinstance(other, CharacteristicBase):
            raise TypeError("Parameter `other` must be of type `CharacteristicBase`.")
        return (
            self.slug == other.slug
            and self.description == other.description
            and self.sub_characteristics == other.sub_characteristics
        )

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
        """Sets unique slug referring to given characteristic."""
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
        """Setter for description method."""
        # add some checks for "description"-style
        self.__description = description

    @property
    def sub_characteristics(self) -> Dict[str, "CharacteristicBase"]:
        """Returns a dict of sub-characteristics.

        Returns:
            Dict[str, CharacteristicBase]: Key represent the slug and the value of the
                                           dict consists of the related Characteristic,
                                           inheriting from `CharacteristicBase`.
        """
        return self.__sub_characteristics

    @property
    def attributes(self) -> CharacteristicAttributes:
        """Returns attributes of characteristic."""
        return self.__attributes

    @property
    def environment(self) -> Dict[str, Any]:
        """Returns environment of characteristic."""
        return self.__environment

    @environment.setter
    def environment(self, value: Dict[str, Any]) -> None:
        self.__environment = value

    def add_sub_characteristic(self, sub_characteristic: "CharacteristicBase") -> None:
        """Add a sub-characteristic.

        Args:
            sub_characteristic (CharacteristicBase): Sub characteristic which will be
                                                     added.
        """
        self.__sub_characteristics[sub_characteristic.slug] = sub_characteristic

    def add_sub_characteristic_list(
        self, sub_characteristic_list: List["CharacteristicBase"]
    ) -> None:
        """Add a list of sub-characteristics.

        Args:
            sub_characteristic_list (List[CharacteristicBase]): Sub characteristics
                                        which will be added.
        """
        for characteristic in sub_characteristic_list:
            self.add_sub_characteristic(characteristic)


GeneratorCheckType = Generator[Tuple[CharacteristicBase, CheckType], None, None]


class Characteristic(CharacteristicBase, metaclass=abc.ABCMeta):
    """Interface for a characteristics."""

    def __init__(
        self,
        slug: str = "",
        description: str = "",
        attributes: CharacteristicAttributes = CharacteristicAttributes(
            runtime=Runtime.DEFAULT
        ),
    ):
        super().__init__(slug, description, attributes)
        self.__slug = slug
        self.__description = description

    def check(self) -> GeneratorCheckType:
        """Checks if given characteristic is already satisfied."""
        no_errors = True
        result_list: List[Tuple[CharacteristicBase, CheckType]] = []
        if self.attributes.runtime != get_current_runtime():
            yield self, CheckType("Skipped, malvm is not running on Windows.", False)
            return
        if self.sub_characteristics:
            for sub_characteristic in self.sub_characteristics.values():
                check_result = sub_characteristic.check()
                if not check_result[-1]:
                    no_errors = False
                result_list.append((sub_characteristic, check_result))
        yield self, CheckType("Summary", no_errors)
        for result in result_list:
            characteristic = result[0]
            yield characteristic, CheckType(*result[1])  # type: ignore

    def fix(self) -> GeneratorCheckType:
        """Satisfies given characteristic."""
        no_errors = True
        result_list: List[Tuple[CharacteristicBase, CheckType]] = []
        if self.attributes.runtime != get_current_runtime():
            yield self, CheckType("Skipped, malvm is not running on Windows.", False)
            return
        if self.sub_characteristics:
            for sub_characteristic in self.sub_characteristics.values():
                check_result = sub_characteristic.fix()
                if not check_result[-1]:
                    no_errors = False
                result_list.append((sub_characteristic, check_result))
        yield self, CheckType("Summary", no_errors)
        for result in result_list:
            yield result[0], CheckType(*result[1])


class LambdaCharacteristic(CharacteristicBase):
    """A LambdaCharacteristic is used as a sub-characteristic.

    LambdaCharacteristics live from function pointers.
    """

    def __init__(
        self,
        slug: str,
        description: str,
        value: Any,
        check_func: Callable[[Any], bool],
        fix_func: Callable[[Any], bool],
        attributes: CharacteristicAttributes = CharacteristicAttributes(
            runtime=Runtime.DEFAULT
        ),
    ):
        """Initializes function pointers of LambdaCharacteristic.

        Args:
            slug(str): Unique identifier of characteristic.
            description(str): Short description of characteristic.
            value(Any): Value used in object for check-/ fix-method.
            check_func(types.FunctionType): Method executed for checks.
                                            Method receives one parameter - value.
            fix_func(types.FunctionType): Method executed for fixes.
                                          Method receives one parameter - value.
        """
        super().__init__(slug, description, attributes)
        self.__check = check_func
        self.__fix = fix_func
        self.__value = value

    def check(self) -> CheckType:
        """Checks if given characteristic is already satisfied."""
        return CheckType(self.description, self.__check(self.__value))

    def fix(self) -> CheckType:
        """Satisfies given characteristic."""
        return CheckType(self.description, self.__fix(self.__value))

    @property
    def value(self) -> Any:
        """Returns the stored value of object.

        Returns:
            Any: Stored value of object, used for check-/ fix-method.
        """
        return self.__value
