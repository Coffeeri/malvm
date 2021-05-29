"""This module contains the hypervisor VirtualBox."""
import logging
import os
import subprocess
import sys
from typing import Iterable, Optional, List

from .packer import generate_box_template, BoxConfiguration, PackerTemplate
from .vagrant import remove_vbox_vm_and_data, add_vm_to_vagrant_files, get_vm_names_list, \
    get_vagrant_files_folder_path, get_vagrant_box_list, get_vm_id_by_vm_name
from ..hypervisor import Hypervisor
from ....config_loader import VirtualMachineSettings, VirtualMachineNetworkSettings
from .....utils.exceptions import BaseImageExists

log = logging.getLogger()


def install_choco_applications(choco_applications: Optional[List[str]], vm_name: str):
    if choco_applications:
        vm_id = get_vm_id_by_vm_name(vm_name)
        for application in choco_applications:
            log.info(f"Installing {application}...")
            run_command_in_vm(vm_id, f"choco install {application} -y", True)


def install_pip_applications(pip_applications: Optional[List[str]], vm_name: str):
    if pip_applications:
        vm_id = get_vm_id_by_vm_name(vm_name)
        for application in pip_applications:
            log.info(f"Installing {application}...")
            run_command_in_vm(vm_id, f"pip install --no-input {application} ", True)


def run_command_in_vm(vm_id: str, command: str, elevated: bool = False):
    if elevated:
        subprocess.run(
            ["vagrant", "winrm", "-e", "-c", command, vm_id], check=True,
        )
    else:
        subprocess.run(
            ["vagrant", "winrm", "-c", command, vm_id], check=True,
        )


def _set_default_network_in_vm(default_gateway: Optional[str], vm_name: str):
    if default_gateway:
        vm_id = get_vm_id_by_vm_name(vm_name)
        log.info(f"Setting {default_gateway} as default gateway.")
        run_command_in_vm(vm_id, "route DELETE -p 0.0.0.0", elevated=True)
        run_command_in_vm(vm_id,
                          "reg delete HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\PersistentRoutes "
                          "/va /f",
                          elevated=True)
        run_command_in_vm(vm_id, f"route add -p 0.0.0.0 mask 0.0.0.0 {default_gateway}",
                          elevated=True)


def _setup_network(network_configuration: Optional[VirtualMachineNetworkSettings], vm_name: str):
    if network_configuration:
        _set_default_network_in_vm(network_configuration.default_gateway, vm_name)


def _prepare_vagrantfile(vagrantfile_path, vm_name):
    if (vagrantfile_path / "Vagrantfile").exists():
        log.error(f"Virtual Machine {vm_name} has already vagrantfile at {vagrantfile_path}.\n"
                  f"If this was not expected, consider cleaning malvm data or create an issue on gitlab.com.")
        sys.exit(1)
    vagrantfile_path.mkdir(parents=True, exist_ok=True)
    os.chdir(str(vagrantfile_path.absolute()) if vagrantfile_path.is_dir() else str(
        vagrantfile_path.parent.absolute())
             )


def _ensure_vm_running(vm_name: str, vm_id=None):
    if not vm_id:
        vm_id = get_vm_id_by_vm_name(vm_name)
    subprocess.run(["vagrant", "up", vm_id], check=True)


def _install_applications_in_vm(vm_name: str, vm_settings: VirtualMachineSettings):
    log.info("Installing choco applications...")
    install_choco_applications(vm_settings.choco_applications, vm_name)
    log.info("Installing pip applications...")
    install_pip_applications(vm_settings.pip_applications, vm_name)


def revert_snapshot(vm_name, snapshot_name, vm_id=None):
    if not vm_id:
        vm_id = get_vm_id_by_vm_name(vm_name)
    log.debug(f"Revert {vm_name} to snapshot '{snapshot_name}'.")
    subprocess.run(
        ["vagrant", "snapshot", "restore", vm_id, snapshot_name], check=True,
    )


def create_snapshot(vm_name: str, snapshot_name: str, vm_id=None):
    if not vm_id:
        vm_id = get_vm_id_by_vm_name(vm_name)
    log.debug(f"Create snapshot '{snapshot_name}' for {vm_name}.")
    subprocess.run(
        ["vagrant", "snapshot", "save", vm_id, snapshot_name], check=True,
    )


class VirtualBoxHypervisor(Hypervisor):

    def build_base_image(self, config: BoxConfiguration):
        if not self.__base_image_exists(config.vagrant_box_name):
            log.debug(f"Try to build image {config.vagrant_box_name} with configuration {config}.")
            image = BaseImage(config)
            image.build()
        else:
            raise BaseImageExists("Base image already exists.")

    def __base_image_exists(self, image_name: str) -> bool:
        return image_name in get_vagrant_box_list()

    def build_vm(self, vm_name: str, base_image_name: str, vm_settings: VirtualMachineSettings):
        log.info(f"Building Virtual Machine {vm_name}...")
        log.debug(f"Current base images dict: {self._base_images}")
        base_image_settings = self._base_images[base_image_name]
        vagrantfile_path = get_vagrant_files_folder_path() / vm_name
        _prepare_vagrantfile(vagrantfile_path, vm_name)
        log.debug(f"Building vm {vm_name} with base_image_settings {base_image_settings}.")
        box_template = generate_box_template(base_image_name, base_image_settings)
        PackerTemplate(box_template).init_vagrantfile(vm_name, vm_settings)
        log.debug(f"Starting first time VM {vm_name} with `vagrant up`.")
        add_vm_to_vagrant_files(vm_name, vagrantfile_path)
        subprocess.run(["vagrant", "up"], check=True)
        _install_applications_in_vm(vm_name, vm_settings)
        subprocess.run(
            ["vagrant", "halt"], check=True,
        )

    def initiate_first_boot(self, vm_name: str, vm_settings: VirtualMachineSettings):
        self.start_vm(vm_name)
        # TODO if hardening = True in config
        # log.debug(f"Running malvm fix on {vm_name}.")
        # subprocess.run(
        #     ["vagrant", "winrm", "-e", "-c", "malvm fix"], check=True,
        # )
        _setup_network(vm_settings.network_configuration, vm_name)
        create_snapshot(vm_name, "clean-state")

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
        vm_id = get_vm_id_by_vm_name(vm_name)
        subprocess.run(
            ["vagrant", "suspend", vm_id], check=True,
        )

    def reset_vm(self, vm_name: str):
        revert_snapshot(vm_name, "clean_state")

    def destroy_vm(self, vm_name: str):
        remove_vbox_vm_and_data(vm_name)

    def fix_vm(self, vm_name: str):
        vm_id = get_vm_id_by_vm_name(vm_name)
        run_command_in_vm(vm_id, "malvm fix", True)

    def get_virtual_machines_names_iter(self) -> Iterable[str]:
        return get_vm_names_list()


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
