"""This module contains helper methods for controlling and communicate with Vagrant, building virtual machines."""
import csv
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Iterable, Tuple, Any

from ....config_loader import VirtualMachinesType
from .....utils.helper_methods import remove_path_with_success, edit_key_in_json_file, get_config_root


def delete_vagrant_boxes():
    # CAN: only delete if box exists not in `vagrant box list --machine-readable`
    subprocess.run(
        ["vagrant", "box", "remove", "malvm-win-10", "--all"], check=True,
    )


def _clean_malvm_data(clean_paths: List[Path], clean_soft: bool):
    destroy_virtual_machines()
    delete_vagrantfiles_data()
    if not clean_soft:
        delete_vagrant_boxes()
        delete_malvm_data_paths(clean_paths)


def delete_vagrantfiles_data():
    remove_path_with_success(str(get_vagrant_files_json_path()))
    remove_path_with_success(str(get_vagrant_files_folder_path()))


def delete_malvm_data_paths(clean_paths: List[Path]):
    for path in clean_paths:
        remove_path_with_success(str(path.absolute()))


def destroy_virtual_machines():
    for vm_id, vagrantfile_path in get_vm_id_vagrantfile_path():
        destroy_virtual_machine(vm_id)
        remove_path_with_success(vagrantfile_path)


def destroy_virtual_machine(vm_id: str):
    subprocess.run(
        ["vagrant", "destroy", "--force", vm_id], check=True,
    )


def remove_vbox_vm_and_data(vm_name: str):
    vm_id = get_vm_ids_dict()[vm_name]
    destroy_virtual_machine(vm_id)
    remove_path_with_success(str(get_vagrant_files_folder_path() / vm_name))
    remove_vm_from_vagrant_files(vm_name)


def add_vm_to_vagrant_files(name: str, vagrant_parent_path: Path):
    edit_key_in_json_file(
        key=name,
        value=str(vagrant_parent_path.absolute() / "Vagrantfile"),
        json_file_path=get_vagrant_files_json_path(),
    )


def get_vm_ids_dict() -> Dict[str, str]:
    vms_with_id = {}
    for vm_status in get_vm_status():
        vm_name = Path(vm_status["vagrant_file_path"]).parent.name
        vms_with_id[vm_name] = vm_status["machine-id"]
    return vms_with_id


def get_vm_id_by_vm_name(vm_name):
    return get_vm_ids_dict()[vm_name]


def get_vm_names_list() -> Iterable[str]:
    return list(get_vm_ids_dict().keys())


def get_vm_id_vagrantfile_path() -> Iterable[Tuple[str, str]]:
    for vm_status in get_vm_status():
        yield vm_status["machine-id"], vm_status["vagrant_file_path"]


def get_vm_status() -> List[Dict[str, str]]:
    vagrant_file_paths = [
        path for _, path in get_existing_vagrant_files_paths_iterable()
    ]
    malvm_vm_status_purged = []
    for status in __get_vagrant_global_status():
        if status["vagrant_file_path"] in vagrant_file_paths:
            malvm_vm_status_purged.append(status)
    return malvm_vm_status_purged


def filter_existing_vms_from_config(vms_config: VirtualMachinesType) -> VirtualMachinesType:
    existing_vms = get_vm_names_list()
    return {vm_name: vm_config for vm_name, vm_config in vms_config.items() if vm_name not in existing_vms}


def read_json_file(path: Path) -> Any:
    """Returns json of a given file."""
    with path.open(mode="r") as json_file:
        return json.load(json_file)


def remove_vm_from_vagrant_files(vm_name: str):
    remove_key_from_json_file(vm_name, get_vagrant_files_json_path())


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
