import subprocess
from pathlib import Path
from typing import List

from .box_template import BoxConfiguration
from .helper_methods import remove_path_with_success, get_vagrant_files_json_path, \
    get_vagrant_files_folder_path, get_vm_id_vagrantfile_path, get_vm_ids_dict, remove_vm_from_vagrant_files


class VirtualMachine:
    ...


class Hypervisor:
    ...


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


def remove_vm_and_data(vm_name: str):
    vm_id = get_vm_ids_dict()[vm_name]
    destroy_virtual_machine(vm_id)
    remove_path_with_success(str(get_vagrant_files_folder_path() / vm_name))
    remove_vm_from_vagrant_files(vm_name)
