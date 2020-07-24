"""This Module contains helper methods, used by an Package."""
import json
import sys
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Returns the data dir in project."""
    return get_project_root() / "data"


def get_config_root() -> Path:
    """Returns path for config and temp files."""
    platform = sys.platform.lower()
    if platform in ["linux", "linux2", "darwin"]:
        config_path = Path.home() / ".local/share/malvm"
    elif platform == "windows":
        config_path = Path.home() / "/AppData/Local/malvm"
    else:
        raise OSError(f"Your platform <{platform}> is not supported by malvm.")

    if not config_path.exists():
        config_path.mkdir(parents=True)
    return config_path


def get_vm_malvm_egg() -> Path:
    """Returns path for malvm package, used for malvm installation on vms."""
    return get_config_root() / "malvm.egg"


def read_json_file(path: Path) -> Any:
    """Returns json of a given file."""
    with path.open(mode="r") as json_file:
        return json.load(json_file)
