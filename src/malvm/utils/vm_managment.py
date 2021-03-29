"""This module contains classes and functions for virtual machine management."""
import logging
import os
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import List, Dict, Iterable, Tuple, Optional

from .box_template import BoxConfiguration, PackerTemplate
from .exceptions import BaseImageExists
from .helper_methods import remove_path_with_success, get_vagrant_files_json_path, \
    get_vagrant_files_folder_path, remove_vm_from_vagrant_files, \
    get_data_dir, get_vagrant_box_list, edit_key_in_json_file, get_existing_vagrant_files_paths_iterable, \
    __get_vagrant_global_status
from .metaclasses import SingletonMeta
from ..controller.config_loader import VirtualMachineSettings, BaseImageSettings, VirtualMachinesType

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


class Hypervisor(metaclass=SingletonMeta):
    def __init__(self, base_images: Dict[str, Optional[BaseImageSettings]] = {}):
        self._base_images = base_images.copy()

    def set_base_images_dict(self, base_images: Dict[str, BaseImageSettings]):
        self._base_images = base_images.copy()

    def build_base_image(self, config: BoxConfiguration):
        raise NotImplementedError

    def __base_image_exists(self, image_name: str) -> bool:
        raise NotImplementedError

    def build_vm(self, vm_name, base_image_name: str, vm_settings: VirtualMachineSettings):
        raise NotImplementedError

    def initiate_first_boot(self, vm_name):
        raise NotImplementedError

    def start_vm(self, vm_name):
        raise NotImplementedError

    def stop_vm(self, vm_name: str):
        raise NotImplementedError

    def reset_vm(self, vm_name: str):
        raise NotImplementedError

    def destroy_vm(self, vm_name: str):
        raise NotImplementedError

    def fix_vm(self, vm_name: str):
        raise NotImplementedError

    def get_virtual_machines_names_iter(self) -> Iterable[str]:
        raise NotImplementedError


class VirtualBoxHypervisor(Hypervisor):

    def __init__(self, base_images: Dict[str, Optional[BaseImageSettings]] = {}):
        super().__init__(base_images)

    def build_base_image(self, config: BoxConfiguration):
        if not self.__base_image_exists(config.vagrant_box_name):
            log.debug(f"Try to build image {config.vagrant_box_name} with configuration {config}.")
            image = BaseImage(config)
            self._base_images[config.vagrant_box_name] = image
            image.build()
        else:
            raise BaseImageExists("Base image already exists.")

    def __base_image_exists(self, image_name: str) -> bool:
        return image_name in get_vagrant_box_list()

    def build_vm(self, vm_name: str, base_image_name: str, vm_settings: VirtualMachineSettings):
        log.debug(f"Current base images dict: {self._base_images}")
        base_image_settings = self._base_images[
            base_image_name]
        vagrantfile_path = get_vagrant_files_folder_path() / vm_name
        if (vagrantfile_path / "Vagrantfile").exists():
            log.error(f"Virtual Machine {vm_name} has already vagrantfile at {vagrantfile_path}.\n"
                      f"If this was not expected, consider cleaning malvm data or create an issue on gitlab.com.")
            sys.exit(1)

        log.info(f"Build Virtual Machine {vm_name}.")
        vagrantfile_path.mkdir(parents=True, exist_ok=True)

        os.chdir(str(vagrantfile_path.absolute()) if vagrantfile_path.is_dir() else str(
            vagrantfile_path.parent.absolute())
                 )
        log.debug(f"Building vm {vm_name} with base_image_settings {base_image_settings}.")
        box_template = generate_box_template(base_image_name, base_image_settings)
        PackerTemplate(box_template).init_vagrantfile(vm_name, vm_settings)
        log.debug(f"Starting first time VM {vm_name} with `vagrant up`.")
        add_vm_to_vagrant_files(vm_name, vagrantfile_path)
        subprocess.run(
            ["vagrant", "up"], check=True,
        )
        log.debug(f"Shutting down VM {vm_name} with `vagrant halt`.")
        subprocess.run(
            ["vagrant", "halt"], check=True,
        )

    def initiate_first_boot(self, vm_name: str):
        log.debug(f"Starting VM {vm_name} with `vagrant up`.")
        subprocess.run(
            ["vagrant", "up"], check=True,
        )
        log.debug(f"Running malvm fix on {vm_name}.")
        subprocess.run(
            ["vagrant", "winrm", "-e", "-c", "malvm fix"], check=True,
        )
        log.debug(f"Save clean-state snapshot for {vm_name}.")
        subprocess.run(
            ["vagrant", "snapshot", "save", "clean-state"], check=True,
        )

    def start_vm(self, vm_name):
        vagrantfile_path = get_vagrant_files_folder_path() / vm_name
        if not vagrantfile_path.exists():
            log.error(f"Virtual Machine {vm_name} does not exist.")
        else:
            log.info(f"Start Virtual Machine {vm_name}.")
            os.chdir(str(vagrantfile_path.absolute()))
            subprocess.run(
                ["vagrant", "up"], check=True,
            )

    def stop_vm(self, vm_name: str):
        vm_id = get_vm_ids_dict()[vm_name]
        subprocess.run(
            ["vagrant", "suspend", vm_id], check=True,
        )

    def reset_vm(self, vm_name: str):
        vm_id = get_vm_ids_dict()[vm_name]
        subprocess.run(
            ["vagrant", "snapshot", "restore", vm_id, "clean-state"], check=True,
        )

    def destroy_vm(self, vm_name: str):
        remove_vbox_vm_and_data(vm_name)

    def fix_vm(self, vm_name: str):
        vm_id = get_vm_ids_dict()[vm_name]
        subprocess.run(
            ["vagrant winrm -e -c malvm fix", vm_id], check=True,
        )

    def get_virtual_machines_names_iter(self) -> Iterable[str]:
        return get_vm_names_list()


class VirtualMachineManager(metaclass=SingletonMeta):
    def __init__(self, hypervisor: Hypervisor = VirtualBoxHypervisor()):
        self.__hypervisor = hypervisor
        self.__vms_config: Dict[str, VirtualMachineSettings] = {}
        self.__base_images_config: Dict[str, BaseImageSettings] = {}

    def vm_exists(self, vm_name: str) -> bool:
        return vm_name in list(self.get_virtual_machines_names_iter())

    def set_config(self, vms_config: Dict[str, VirtualMachineSettings],
                   base_images_config: Dict[str, BaseImageSettings]):
        self.__vms_config = vms_config
        self.__base_images_config = base_images_config
        self.__hypervisor.set_base_images_dict(self.__base_images_config)

    def __get_default_vm_setting(self) -> Optional[VirtualMachineSettings]:
        return self.__vms_config.get("default", None)

    def set_hypervisor(self, hypervisor: Hypervisor):
        self.__hypervisor = hypervisor
        self.__hypervisor.set_base_images_dict(self.__base_images_config)

    def get_virtual_machines_names_iter(self) -> Iterable[str]:
        return self.__hypervisor.get_virtual_machines_names_iter()

    def build_base_image(self, config: BoxConfiguration):
        self.__hypervisor.build_base_image(config)

    def generate_box_config_by_base_image_name(self, base_image_name: str) -> BoxConfiguration:
        base_images = self.__base_images_config
        if base_image_name not in base_images.keys():
            log.error(f"Baseimage {base_image_name} was not defined in "
                      f"configuration file.")
            sys.exit(1)
        return BoxConfiguration(
            packer_template_path=(PACKER_PATH / f"{base_images[base_image_name].template}.json"),
            packer_box_name=f"{base_images[base_image_name].template}_virtualbox.box",
            vagrant_box_name=base_image_name,
            username=base_images[base_image_name].username,
            password=base_images[base_image_name].password,
            computer_name=base_images[base_image_name].computer_name,
            language_code=base_images[base_image_name].language_code,
        )

    def build_vm(self, vm_name: str, base_image_name: str):
        vm_settings = self.__vms_config.get(vm_name, self.__get_default_vm_setting())
        if vm_settings:
            log.debug(f"VMManager: Building VM name: {vm_name}, base_image_name: {base_image_name}.")
            self.__hypervisor.build_vm(vm_name, base_image_name, vm_settings)

    def build_vms_in_config(self):
        for vm_name, vm_setting in self.__vms_config.items():
            if vm_name is not "default" and not self.vm_exists(vm_name):
                log.debug(f"Building VM from config [{vm_name}]...")
                self.build_vm(vm_name, vm_setting.base_image_name)

    def build_base_images_in_config(self):
        pass

    def initiate_first_boot(self, vm_name: str):
        vm_settings = self.__vms_config.get(vm_name, self.__get_default_vm_setting())
        if vm_settings:
            self.__hypervisor.initiate_first_boot(vm_name)

    def start_vm(self, vm_name: str):
        self.__hypervisor.start_vm(vm_name)

    def stop_vm(self, vm_name: str):
        self.__hypervisor.stop_vm(vm_name)

    def reset_vm(self, vm_name: str):
        self.__hypervisor.reset_vm(vm_name)

    def destroy_vm(self, vm_name: str):
        self.__hypervisor.destroy_vm(vm_name)

    def fix_vm(self, vm_name: str):
        self.__hypervisor.fix_vm(vm_name)


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
    else:
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
