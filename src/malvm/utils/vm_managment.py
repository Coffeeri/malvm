"""This module contains classes and functions for virtual machine management."""
import logging
import subprocess
from enum import Enum
from pathlib import Path
from typing import List, Dict, Iterable, Tuple

from .box_template import BoxConfiguration, PackerTemplate
from .helper_methods import remove_path_with_success, get_vagrant_files_json_path, \
    get_vagrant_files_folder_path, remove_vm_from_vagrant_files, \
    get_data_dir, edit_key_in_json_file, get_existing_vagrant_files_paths_iterable, \
    __get_vagrant_global_status
from ..controller.config_loader import BaseImageSettings, VirtualMachinesType

log = logging.getLogger()
PACKER_PATH = get_data_dir() / "packer"


class BaseImage:
    def __init__(self, config: BoxConfiguration):
        self.config = config
        log.debug(f"Init base image {config.vagrant_box_name} with config {config}.")

    def build(self):
        log.debug(self.config)
        packer_template = PackerTemplate(self.config)
        packer_template.configure()
        packer_template.build()
        packer_template.add_to_vagrant()


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


class OperatingSystem(Enum):
    """Enum defining the execution-time of a characteristic."""

    WINDOWS_10 = 1


def generate_box_template(base_image_name: str, base_image_settings: BaseImageSettings):
    if base_image_settings.template == "windows_10":
        return BoxConfiguration(
            packer_template_path=(PACKER_PATH / "windows_10.json"),
            packer_box_name=f"windows_10_{base_image_name}_virtualbox.box",
            vagrant_box_name=base_image_name,
            username=base_image_settings.username,
            password=base_image_settings.password,
            computer_name=base_image_settings.computer_name,
            language_code=base_image_settings.language_code,
        )
    raise NotImplementedError(f"Base-Image template {base_image_settings.template} "
                              f"does not exist/ is not supported.")


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
