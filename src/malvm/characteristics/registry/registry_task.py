"""This module contains classes for characteristics of registry entries.

Classes:
    RegistryVBCharacteristic: Checks and Fixes registry entries referring to VirtualBox.
"""
import logging
import platform
from enum import Enum
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple, Union

from ...controller.virtual_machine.hypervisor.virtualbox.vagrant import \
    read_json_file
from ...utils.helper_methods import get_project_root
from ..abstract_characteristic import Characteristic, LambdaCharacteristic

log = logging.getLogger()

try:
    # type: ignore
    from winreg import (  # type: ignore  # pylint: disable=E0401,I0023,I0021
        HKEY_LOCAL_MACHINE,
        OpenKey,
        KEY_ALL_ACCESS,
        QueryInfoKey,
        EnumKey,
        DeleteKey,
        KEY_WOW64_64KEY,
        KEY_WOW64_32KEY,
        REG_SZ,
        QueryValueEx,
        CreateKey,
        SetValueEx,
    )
except ModuleNotFoundError:
    pass
    # print_warning("Registry characteristic can be only run on Windows machines.")


class RegistryVBCharacteristic(Characteristic):
    """Checks and Fixes for existence of identifiable registry entries."""

    def __init__(self) -> None:
        super().__init__("RVB", "Registry entries identifying VirtualBox.")
        sub_characteristics = sub_characteristics_virtualbox()
        self.add_sub_characteristic_list(list(sub_characteristics))


class RegistryAction(Enum):
    """Action to be execute in fix stage."""

    REMOVE = 1
    CHANGE = 2


class RegistryTask(NamedTuple):
    """Data of a registry sub characteristic instance."""

    slug: str
    action: RegistryAction
    hypervisor: str
    key: str
    parameter: Optional[str]
    value: Optional[str]


def check_registry_key(task: RegistryTask) -> bool:
    """Checks if registry task is already satisfied."""
    if platform.system() != "Windows":
        return False
    if task.action == RegistryAction.REMOVE:
        return not check_registry_key_exists(task)
    return check_registry_key_value(task)


def fix_registry_key(task: RegistryTask) -> bool:
    """Fixes registry key entry."""
    if platform.system() != "Windows":
        return False
    if task.action == RegistryAction.REMOVE:
        remove_key(task)
    elif task.action == RegistryAction.CHANGE:
        set_key_value(task)
    return check_registry_key(task)


def check_registry_key_exists(task: RegistryTask) -> bool:
    """Returns True if key exists in registry."""
    try:
        key_base, key_path = split_key(task.key)
        OpenKey(key_base, key_path)
    except FileNotFoundError:
        return False
    return True


def check_registry_key_value(task: RegistryTask) -> bool:
    """Returns true if the value of key is set in registry."""
    key_base, key_path = split_key(task.key)
    try:
        key = OpenKey(key_base, key_path)
        key_value = QueryValueEx(key, task.parameter)[0]
        key_value = normalize_key_value(key_value)
        if key_value == task.value:
            return True
    except FileNotFoundError:
        return False
    return False


def normalize_key_value(key_value: Union[str, List[str]]) -> str:
    """Returns normalize string of registry key value."""
    if isinstance(key_value, list):
        key_value = "\n".join(key_value)
    return key_value


def split_key(key: str) -> Tuple[int, str]:
    """Returns key-base and remaining key-path."""
    key_base = 0
    key_path = key
    if key.startswith("HKEY_LOCAL_MACHINE\\"):
        key_base = HKEY_LOCAL_MACHINE
        key_path = key_path.replace("HKEY_LOCAL_MACHINE\\", "")
    return key_base, key_path


def set_key_value(task: RegistryTask):
    """Sets value of key.

    If the key does not exist, it will be created.
    Only strings are supported.
    """
    key_base, key_path = split_key(task.key)
    key = CreateKey(key_base, key_path)
    SetValueEx(key, task.parameter, 0, REG_SZ, task.value)


def remove_key(task: RegistryTask) -> None:
    """Removes key recursively in 32Bit and 64Bit mode."""
    key_base, key_path = split_key(task.key)
    arch_keys = [KEY_WOW64_32KEY, KEY_WOW64_64KEY]
    for arch_key in arch_keys:
        try:
            delete_sub_key(key_base, key_path, arch_key)
        except OSError as exception:
            log.exception(exception)


def delete_sub_key(key0: int, current_key: str, arch_key: int = 0) -> None:
    """Deletes registry key including all sub-keys."""
    try:
        open_key = OpenKey(key0, current_key, 0, KEY_ALL_ACCESS | arch_key)
        info_key = QueryInfoKey(open_key)
        for _ in range(0, info_key[0]):
            sub_key = EnumKey(open_key, 0)
            try:
                DeleteKey(open_key, sub_key)
            except OSError:
                delete_sub_key(key0, "\\".join([current_key, sub_key]), arch_key)
        DeleteKey(open_key, "")
        open_key.Close()
    except OSError as exception:
        log.debug(f"Key {current_key} does not exist. OSErrr-exception: {exception}")


def sub_characteristics_virtualbox() -> List[LambdaCharacteristic]:
    """Returns list of sub-characteristics each responsible for one registry key."""
    data_path = Path(get_project_root() / "data/registry.json")
    data: List[Dict[str, str]] = read_json_file(data_path)
    registry_characteristics: List[LambdaCharacteristic] = []
    for entry in data:
        registry_task = RegistryTask(
            slug=entry["slug"],
            action=RegistryAction[entry["action"].upper()],
            hypervisor=entry["hypervisor"],
            key=entry["key"],
            parameter=None if "parameter" not in entry else entry["parameter"],
            value=None if "value" not in entry else entry["value"],
        )
        description = f"Registry entry identifying VirtualBox {registry_task.key}"
        characteristic = LambdaCharacteristic(
            registry_task.slug,
            description,
            registry_task,
            check_registry_key,
            fix_registry_key,
        )
        registry_characteristics.append(characteristic)
    return registry_characteristics
