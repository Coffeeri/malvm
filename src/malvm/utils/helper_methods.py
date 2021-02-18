"""This Module contains helper methods, used by an Package."""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Tuple, List, Dict


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
    elif platform in ["windows", "win32"]:
        config_path = Path.home().absolute() / "/AppData/Local/malvm"
    else:
        raise OSError(f"Your platform <{platform}> is not supported by malvm.")

    if not config_path.exists():
        config_path.mkdir(parents=True)
    return config_path


def get_logfile_path() -> Path:
    path = get_config_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_vm_malvm_package_file() -> Path:
    """Returns path for malvm package, used for malvm installation on vms."""
    return get_config_root() / "malvm.tar.gz"


def read_json_file(path: Path) -> Any:
    """Returns json of a given file."""
    with path.open(mode="r") as json_file:
        return json.load(json_file)


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


def remove_vm_from_vagrant_files(vm_name: str):
    remove_key_from_json_file(vm_name, get_vagrant_files_json_path())


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


def remove_key_from_json_file(key: Any, json_file_path: Path):
    if json_file_path.exists():
        with json_file_path.open() as opened_file:
            data = json.load(opened_file)
        data.pop(key)
        with json_file_path.open(mode="w") as opened_file:
            json.dump(data, opened_file)


def get_existing_vagrant_files_paths_iterable() -> Iterable[Tuple[str, Path]]:
    data = read_json_file(get_vagrant_files_json_path())
    for vm_name, vagrantfile_path in data.items():
        yield vm_name, vagrantfile_path


def get_vagrant_files_json_path() -> Path:
    path = get_config_root() / "vagrantfiles.json"
    if not path.exists():
        path.write_text("{}")
    return path


def get_vagrant_files_folder_path() -> Path:
    return Path(get_config_root() / "vagrantfiles/")


def __get_vagrant_global_status() -> List[Dict[str, str]]:
    result = subprocess.run(
        ["vagrant", "global-status", "--prune", "--machine-readable"],
        stdout=subprocess.PIPE,
        check=True,
    )
    reader = decode_vagrant_output(result)
    vm_collection = []
    current_vm = []
    for row in reader:
        if len(row) == 4:
            current_vm.append(row[3])
            if len(current_vm) == 4:
                vm_collection.append(
                    {
                        "machine-id": current_vm[0],
                        "provider-name": current_vm[1],
                        "provider-home": current_vm[2],
                        "vagrant_file_path": current_vm[2] + "/Vagrantfile",
                        "state": current_vm[3],
                    }
                )
                current_vm = []
    return vm_collection


def get_vagrant_box_list() -> List[str]:
    result = subprocess.run(
        ["vagrant", "box", "list", "--machine-readable"],
        stdout=subprocess.PIPE,
        check=True,
    )
    reader = decode_vagrant_output(result)
    base_images = []
    for row in reader:
        if len(row) == 4 and row[2] == "box-name":
            base_images.append(row[3])
    return base_images


def decode_vagrant_output(result):
    result_decoded = result.stdout.decode("utf-8")
    reader = csv.reader(result_decoded.split("\n"), delimiter=",")
    return reader
