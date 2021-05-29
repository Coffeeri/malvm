"""This module contains the virtual machine manager."""
import logging
import sys
from typing import Dict, Optional, Iterable, List

from ..config_loader import VirtualMachineSettings, BaseImageSettings
from .hypervisor.hypervisor import Hypervisor
from .hypervisor.virtualbox.virtualbox import VirtualBoxHypervisor
from ...utils.exceptions import BaseImageExists
from ...utils.metaclasses import SingletonMeta
from .hypervisor.virtualbox.packer import PACKER_PATH, BoxConfiguration

log = logging.getLogger()


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

    # TODO Refactor into packer.py, image should be handled by VirtualBox and BoxConfiguration by packer.py
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
            log.debug(f"VM-Manager: Building VM name: {vm_name}, base_image_name: {base_image_name}.")
            self.__hypervisor.build_vm(vm_name, base_image_name, vm_settings)

    def build_vms_in_config(self):
        for vm_name, vm_setting in self.__vms_config.items():
            if vm_name != "default" and not self.vm_exists(vm_name):
                log.debug(f"Building VM from config [{vm_name}]...")
                self.build_vm(vm_name, vm_setting.base_image_name)

    def build_base_images_in_config(self):
        for base_image in self.__base_images_config.keys():
            box_config = self.generate_box_config_by_base_image_name(base_image)
            try:
                self.build_base_image(box_config)
            except BaseImageExists:
                log.debug(f"Base image {base_image} already exists.")

    def initiate_first_boot(self, vm_name: str):
        vm_settings = self.__vms_config.get(vm_name, self.__get_default_vm_setting())
        if vm_settings:
            self.__hypervisor.initiate_first_boot(vm_name, vm_settings)

    def start_vm(self, vm_name: str):
        self.__hypervisor.start_vm(vm_name)

    def stop_vm(self, vm_name: str):
        self.__hypervisor.stop_vm(vm_name)

    def reset_vm(self, vm_name: str):
        self.__hypervisor.reset_vm(vm_name)

    def destroy_vm(self, vm_name: str):
        self.__hypervisor.destroy_vm(vm_name)

    def fix_vm(self, vm_name: str, characteristics: Optional[List[str]]):
        self.__hypervisor.fix_vm(vm_name, characteristics)
