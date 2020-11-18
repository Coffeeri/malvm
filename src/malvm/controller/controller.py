"""This module contains the controller for checks and fixes.

Classes:
    Controller: Controls the checks and fixes of characteristics.
"""
import inspect
import pkgutil
import sys
from enum import Enum
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterator

from ..characteristics.abstract_characteristic import (
    CharacteristicBase,
    CheckResult,
    Runtime,
    Characteristic,
)
from ..utils.metaclasses import SingletonMeta


def load_characteristics_by_path(path: str) -> Iterator[Characteristic]:
    package = "malvm.characteristics"
    for (_, name, _) in pkgutil.iter_modules([path]):
        imported_module = import_module("." + name, package=package)
        imported_module = import_module(f"{package}.{name}")
        for i in dir(imported_module):
            attribute = getattr(imported_module, i)
            if (
                inspect.isclass(attribute)
                and issubclass(attribute, Characteristic)
                and attribute is not Characteristic
            ):
                setattr(sys.modules[__name__], name, attribute)
                yield attribute()


def get_sub_characteristics(
    characteristic: CharacteristicBase,
) -> Iterator[CharacteristicBase]:
    if characteristic.sub_characteristics:
        yield from characteristic.sub_characteristics.values()


class CharacteristicAction(Enum):
    """Decides which whether check or fix will be executed."""

    CHECK = 1
    FIX = 2


def action_on_characteristic(
    characteristic: CharacteristicBase, action: CharacteristicAction
) -> CheckResult:
    if action == CharacteristicAction.CHECK:
        yield from characteristic.check()
    elif action == CharacteristicAction.FIX:
        yield from characteristic.fix()


class Controller(metaclass=SingletonMeta):
    """The controller loads and manages all characteristics."""

    def __init__(self) -> None:
        self.characteristics_path = str(
            (Path(__file__).parent.parent / "characteristics")
        )
        self.characteristics: Dict[str, CharacteristicBase] = {}
        self.__load_and_add_characteristics()

    def __load_and_add_characteristics(self) -> None:
        for characteristic in load_characteristics_by_path(self.characteristics_path):
            self.add_characteristic(characteristic)

    def add_characteristic(self, characteristic: CharacteristicBase) -> None:
        self.characteristics[characteristic.slug] = characteristic

    def __get_all_characteristics_dict(self) -> Dict[str, CharacteristicBase]:
        return {
            characteristic.slug: characteristic
            for characteristic in self.__get_all_characteristics()
        }

    def __get_all_characteristics(self) -> Iterator[CharacteristicBase]:
        for characteristic in self.characteristics.values():
            yield characteristic
            yield from get_sub_characteristics(characteristic)

    def get_all_checks_results(self) -> CheckResult:
        for characteristic in self.get_characteristic_list():
            yield from self.get_check_results(characteristic.slug)

    def get_pre_boot_checks_results(self, environment: Dict[str, Any]) -> CheckResult:
        for characteristic in self.get_characteristic_list(False, Runtime.PRE_BOOT):
            self.characteristics[characteristic.slug].environment = environment
            yield from self.get_check_results(characteristic.slug)

    def get_check_results(self, slug_searched: str) -> CheckResult:
        yield from self.__action_on_characteristic_with_results(
            slug_searched, CharacteristicAction.CHECK
        )

    def apply_all_fixes_get_results(self) -> CheckResult:
        for characteristic in self.get_characteristic_list():
            yield from self.apply_fix_get_results(characteristic.slug)

    def apply_pre_boot_fixes(self, environment: Dict[str, Any]) -> CheckResult:
        for characteristic in self.get_characteristic_list(False, Runtime.PRE_BOOT):
            self.characteristics[characteristic.slug].environment = environment
            yield from self.apply_fix_get_results(characteristic.slug)

    def apply_fix_get_results(self, slug_searched: str) -> CheckResult:
        yield from self.__action_on_characteristic_with_results(
            slug_searched, CharacteristicAction.FIX
        )

    def __action_on_characteristic_with_results(
        self, slug_searched: str, action: CharacteristicAction
    ) -> CheckResult:
        characteristic = self.__get_all_characteristics_dict().get(slug_searched, None)
        if characteristic:
            yield from action_on_characteristic(characteristic, action)
        else:
            raise ValueError("Characteristic was not found.")

    def get_characteristic_list(
        self,
        include_sub_characteristics: bool = False,
        selected_runtime: Optional[Runtime] = Runtime.DEFAULT,
    ) -> List[CharacteristicBase]:
        if include_sub_characteristics:
            characteristics = self.__get_all_characteristics()
        else:
            characteristics = iter(self.characteristics.values())

        return [
            characteristic
            for characteristic in characteristics
            if (
                (characteristic.attributes.runtime == selected_runtime)
                or (selected_runtime is None)
            )
        ]
