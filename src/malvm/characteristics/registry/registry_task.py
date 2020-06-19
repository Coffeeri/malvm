"""This module contains classes for characteristics of registry entries.

Classes:
    RegistryVBCharacteristic: Checks and Fixes registry entries referring to VirtualBox.
"""
from pathlib import Path
from typing import List, Dict, Tuple
from _winreg import *

from ..abstract_characteristic import Characteristic, LambdaCharacteristic
from ...utils.helper_methods import get_project_root, read_json_file


def check_reg_key(key: str) -> bool:
    base_key = None
    if key.startswith("HKEY_LOCAL_MACHINE\\"):
        base_key = HKEY_LOCAL_MACHINE


def fix_reg_key(key_value: Tuple[str, str]) -> bool:
    pass


def sub_characteristics_virtualbox() -> List[LambdaCharacteristic]:
    """Returns list of sub-characteristics each responsible for one registry key."""
    data_path = Path(get_project_root() / "data/registry.json")
    data: List[Dict[str, str]] = read_json_file(data_path)
    registry_characteristics: List[LambdaCharacteristic] = []
    for entry in data:
        description = f"Registry entry identifying VirtualBox {entry['key']}"
        characteristic = LambdaCharacteristic(
            entry["slug"], description, entry["key"], check_reg_key, fix_reg_key
        )
        registry_characteristics.append(characteristic)
    return registry_characteristics


class RegistryVBCharacteristic(Characteristic):
    """Checks and Fixes for existence of identifiable registry entries."""

    def __init__(self) -> None:
        super().__init__("RVB", "Registry entries identifying VirtualBox.")
        sub_characteristics = sub_characteristics_virtualbox()
        self.add_sub_characteristic_list(list(sub_characteristics))
