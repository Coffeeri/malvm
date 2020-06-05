"""This module contains classes for characteristics of files and processes.

Classes:
    FileCharacteristic: Checks and Fixes for existence of striking files.
"""
import json
from pathlib import Path
from typing import List, Dict, Union

from ..abstract_characteristic import Characteristic, LambdaCharacteristic
from ...utils.helper_methods import get_project_root


def read_json_file(path: Path) -> Dict[str, Union[str, List[str], List[List[str]]]]:
    """Returns json of a given file.

    Args:
        path (Path): Path to json-file.
    """
    with path.open(mode="r") as json_file:
        return json.load(json_file)


def check_path_not_exists(path: str) -> bool:
    """Returns `True` if path to file/ directory does not exists."""
    return not Path(path).exists()


def remove_path(path: str) -> bool:
    """Removes file or directory.

    After removing the file/ directory, a path check is executed to validated the
    success of removal.

    Args:
        path(str): Path to file/ directory.

    Returns:
        bool: Returns True if file was deleted correctly.
    """
    if check_path_not_exists(path):
        return True
    path_obj = Path(path)
    if path_obj.is_file():
        path_obj.unlink()
    elif path_obj.is_dir():
        path_obj.rmdir()
    return check_path_not_exists(path)


def get_virtualbox_files():
    """Returns all files uncovering VirtualBoxs existencee."""
    return read_json_file(Path(get_project_root() / "data/files_virtualbox.json"))[
        "files"
    ]


def get_vmware_files():
    """Returns all files uncovering VirtualBoxs existencee."""
    return read_json_file(Path(get_project_root() / "data/files_vmware.json"))["files"]


def sub_characteristics_virtualbox() -> List[LambdaCharacteristic]:
    """Creates a list of LambdaCharacteristics.

    A new sub characteristic will be created for each File.
    """
    file_characteristics: List[LambdaCharacteristic] = []
    data: List[List[str]] = get_virtualbox_files()
    for slug, file_path in data:
        description = f"File uncovering VirtualBox existence: {file_path}"
        characteristic = LambdaCharacteristic(
            slug, description, file_path, check_path_not_exists, remove_path,
        )
        file_characteristics.append(characteristic)
    return file_characteristics


def sub_characteristics_vmware() -> List[LambdaCharacteristic]:
    """Creates a list of LambdaCharacteristics.

    A new sub characteristic will be created for each File.
    """
    file_characteristics: List[LambdaCharacteristic] = []
    data: List[List[str]] = get_vmware_files()
    for slug, file_path in data:
        description = f"File uncovering VMWare existence: {file_path}"
        characteristic = LambdaCharacteristic(
            slug, description, file_path, check_path_not_exists, remove_path,
        )
        file_characteristics.append(characteristic)
    return file_characteristics


class FileVBCharacteristic(Characteristic):
    """Checks and Fixes for existence of striking files."""

    def __init__(self) -> None:
        super().__init__("FVB", "Files uncovering VirtualBox.")
        sub_characteristics = sub_characteristics_virtualbox()
        self.add_sub_characteristic_list(list(sub_characteristics))


class FileVMWCharacteristic(Characteristic):
    """Checks and Fixes for existence of striking files."""

    def __init__(self) -> None:
        super().__init__("FVMW", "Files uncovering VMWare.")
        sub_characteristics = sub_characteristics_vmware()
        self.add_sub_characteristic_list(list(sub_characteristics))
