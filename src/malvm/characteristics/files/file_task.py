"""This module contains classes for characteristics of files.

Classes:
    FileVBCharacteristic: Checks and Fixes for files referring to VirtualBox.
    FileVMWCharacteristic: Checks and Fixes for files referring to VMWare.
"""
from pathlib import Path
from typing import List

from ...utils.helper_methods import get_project_root, read_json_file
from ..abstract_characteristic import Characteristic, LambdaCharacteristic


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
    try:

        if path_obj.is_file():
            path_obj.unlink()
        elif path_obj.is_dir():
            path_obj.rmdir()
    except PermissionError:
        return False
    return check_path_not_exists(path)


def get_virtualbox_files():
    """Returns all files identifying VirtualBoxs existencee."""
    return read_json_file(
        Path(Path(get_project_root() / "data/files_virtualbox.json")).absolute()
    )["files"]


def get_vmware_files():
    """Returns all files identifying VirtualBoxs existencee."""
    return read_json_file(
        Path(Path(get_project_root() / "data/files_vmware.json")).absolute()
    )["files"]


def sub_characteristics_virtualbox() -> List[LambdaCharacteristic]:
    """Creates a list of LambdaCharacteristics.

    A new sub characteristic will be created for each File.
    """
    file_characteristics: List[LambdaCharacteristic] = []
    data: List[List[str]] = get_virtualbox_files()
    for slug, file_path in data:
        description = f"File identifying VirtualBox existence: {file_path}"
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
        description = f"File identifying VMWare existence: {file_path}"
        characteristic = LambdaCharacteristic(
            slug, description, file_path, check_path_not_exists, remove_path,
        )
        file_characteristics.append(characteristic)
    return file_characteristics


class FileVBCharacteristic(Characteristic):
    """Checks and Fixes for existence of striking files."""

    def __init__(self) -> None:
        super().__init__("FVB", "Files identifying VirtualBox.")
        sub_characteristics = sub_characteristics_virtualbox()
        self.add_sub_characteristic_list(list(sub_characteristics))


class FileVMWCharacteristic(Characteristic):
    """Checks and Fixes for existence of striking files."""

    def __init__(self) -> None:
        super().__init__("FVMW", "Files identifying VMWare.")
        sub_characteristics = sub_characteristics_vmware()
        self.add_sub_characteristic_list(list(sub_characteristics))
