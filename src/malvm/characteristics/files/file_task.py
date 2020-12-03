"""This module contains classes for characteristics of files.

Classes:
    FileVBCharacteristic: Checks and Fixes for files referring to VirtualBox.
    FileVMWCharacteristic: Checks and Fixes for files referring to VMWare.
"""
from pathlib import Path
from typing import List, Iterator

from ...utils.helper_methods import (
    get_project_root,
    read_json_file,
    remove_path_with_success,
    check_path_not_exists,
)
from ..abstract_characteristic import Characteristic, LambdaCharacteristic


class FileVBCharacteristic(Characteristic):
    """Removes files leaking existence of VirtualBox."""

    def __init__(self) -> None:
        super().__init__("FVB", "Files identifying VirtualBox.")
        sub_characteristics = get_sub_characteristics_virtualbox()
        self.add_sub_characteristic_list(list(sub_characteristics))


def get_virtualbox_files() -> List[List[str]]:
    return read_json_file(
        Path(Path(get_project_root() / "data/files_virtualbox.json")).absolute()
    )["files"]


def get_sub_characteristics_virtualbox() -> Iterator[LambdaCharacteristic]:
    for slug, file_path in get_virtualbox_files():
        characteristic = LambdaCharacteristic(
            slug=slug,
            description=f"File identifying VirtualBox existence: {file_path}",
            value=file_path,
            check_func=check_path_not_exists,
            fix_func=remove_path_with_success,
        )
        yield characteristic
