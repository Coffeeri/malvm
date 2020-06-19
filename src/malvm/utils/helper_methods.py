"""This Module contains helper methods, used by an Package."""
import json
from pathlib import Path
from typing import Dict, Union, List


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def read_json_file(path: Path) -> Dict[str, Union[str, List[str], List[List[str]]]]:
    """Returns json of a given file."""
    with path.open(mode="r") as json_file:
        return json.load(json_file)
