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


def add_vm_to_vagrant_files(name: str, vagrant_parent_path: str):
    edit_key_in_json_file(
        key=name,
        value=str(Path(vagrant_parent_path).absolute() / "Vagrantfile"),
        json_file_path=get_vagrant_files_path(),
    )


def edit_key_in_json_file(key: Any, value: Any, json_file_path: Path):
    if json_file_path.exists():
        with json_file_path.open() as file:
            data = json.load(file)
    else:
        json_file_path.touch()
        data = {}
    data[key] = value
    with json_file_path.open(mode="w") as file:
        json.dump(data, file)


def get_existing_vagrantfiles_paths_iterable() -> Iterable[Tuple[str, Path]]:
    data = read_json_file(get_vagrant_files_path())
    for vm_name, vagrantfile_path in data.items():
        yield vm_name, vagrantfile_path


def get_vagrant_files_path() -> Path:
    return get_config_root() / "vagrant_files.json"


def __get_vagrant_global_status() -> List[Dict[str, str]]:
    result = subprocess.run(
        ["vagrant", "global-status", "--prune", "--machine-readable"],
        stdout=subprocess.PIPE,
        check=True,
    )
    result_decoded = result.stdout.decode("utf-8")
    reader = csv.reader(result_decoded.split("\n"), delimiter=",")
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


def get_vm_ids() -> Iterable[str]:
    for vm_status in get_vm_status():
        yield vm_status["machine-id"]


def get_vm_id_vagrantfile_path() -> Iterable[Tuple[str, str]]:
    for vm_status in get_vm_status():
        yield vm_status["vagrant_file_path"], vm_status["machine-id"]


def get_vm_status() -> List[Dict[str, str]]:
    vagrant_file_paths = [
        path for _, path in get_existing_vagrantfiles_paths_iterable()
    ]
    malvm_vm_status_purged = []
    for status in __get_vagrant_global_status():
        if status["vagrant_file_path"] in vagrant_file_paths:
            malvm_vm_status_purged.append(status)
    return malvm_vm_status_purged
