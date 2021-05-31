"""This module defines an abstract definition of a hypervisor object."""
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ....utils.metaclasses import SingletonMeta
from ...config_loader import BaseImageSettings, VirtualMachineSettings
from .virtualbox.packer import BoxConfiguration


class Hypervisor(metaclass=SingletonMeta):
    def __init__(self, base_images: Dict[str, BaseImageSettings] = None):
        self._base_images = base_images.copy() if base_images else {}

    def set_base_images_dict(self, base_images: Dict[str, BaseImageSettings]):
        self._base_images = base_images.copy()

    def build_base_image(self, config: BoxConfiguration):
        raise NotImplementedError

    def __base_image_exists(self, image_name: str) -> bool:
        raise NotImplementedError

    def build_vm(self, vm_name, base_image_name: str, vm_settings: VirtualMachineSettings):
        raise NotImplementedError

    def initiate_first_boot(self, vm_name, vm_settings: VirtualMachineSettings):
        raise NotImplementedError

    def start_vm(self, vm_name):
        raise NotImplementedError

    def stop_vm(self, vm_name: str):
        raise NotImplementedError

    def reset_vm(self, vm_name: str):
        raise NotImplementedError

    def destroy_vm(self, vm_name: str):
        raise NotImplementedError

    def fix_vm(self, vm_name: str, characteristics: Optional[List[str]]):
        raise NotImplementedError

    def get_virtual_machines_names_iter(self) -> Iterable[str]:
        raise NotImplementedError

    def upload_file(self, vm_name: str, local_file_path: Path, remote_file_path: str):
        raise NotImplementedError
