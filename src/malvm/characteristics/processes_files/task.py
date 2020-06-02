"""This module contains classes for characteristics of files and processes.

Classes:
    FileCharacteristic: Checks and Fixes for existence of striking files.
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple

from ..abstract_characteristic import Characteristic


def read_files_file(path: Path) -> List[Dict[str, List[str]]]:
    """Returns json of a given file.

    Args:
        path (Path): Path to json-file.
    """
    with path.open(mode="r") as json_file:
        return json.load(json_file)


class FileCharacteristic(Characteristic):
    """Checks and Fixes for existence of striking files."""

    def check(self) -> List[Tuple[str, bool]]:
        """Checks for existence of striking files."""

        files_data: List[Dict[str, List[str]]] = read_files_file(
            Path("data/files.json")
        )
        results: List[Tuple[str, bool]] = []

        for entry in files_data:
            for hypervisor, files in entry.items():
                for file in files:
                    results.append((f"[{hypervisor}] {file}", not Path(file).exists()))
        return results

    def fix(self) -> None:
        """Fixes striking files."""
