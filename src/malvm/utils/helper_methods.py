"""This Module contains helper methods, used by an Package."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Returns the data dir in project."""
    return get_project_root() / "data"


def get_logfile_path() -> Path:
    path = get_config_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_vm_malvm_package_file() -> Path:
    """Returns path for malvm package, used for malvm installation on vms."""
    return get_config_root() / "malvm.tar.gz"


def remove_path_with_success(path: str) -> bool:
    if check_path_not_exists(path):
        return True
    path_obj = Path(path)
    try:
        if path_obj.is_file():
            path_obj.unlink()
        elif path_obj.is_dir():
            shutil.rmtree(path_obj)
    except PermissionError:
        return False
    return check_path_not_exists(path)


def check_path_not_exists(path: str) -> bool:
    return not Path(path).exists()


def edit_key_in_json_file(key: Any, value: Any, json_file_path: Path):
    if json_file_path.exists():
        with json_file_path.open() as opened_file:
            data = json.load(opened_file)
    else:
        json_file_path.touch()
        data = {}
    data[key] = value
    with json_file_path.open(mode="w") as opened_file:
        json.dump(data, opened_file)


def get_config_root() -> Path:
    platform = sys.platform.lower()
    if platform in ["linux", "linux2", "darwin"]:
        config_path = Path.home() / ".local/share/malvm"
    elif platform in ["windows", "win32"]:
        config_path = Path.home().absolute() / "/AppData/Local/malvm"
    else:
        raise OSError(f"Your platform <{platform}> is not supported by malvm.")

    if not config_path.exists():
        config_path.mkdir(parents=True)
    return config_path


def get_virtual_box_vminfo(vm_name: str):
    result = subprocess.run(
        ["VBoxManage", "showvminfo", vm_name, "--machinereadable"],
        stdout=subprocess.PIPE,
        check=True,
    )
    return result


def run_external_program_no_return(*args):
    subprocess.run(args, check=True)
