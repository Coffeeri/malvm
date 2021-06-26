"""This module contains helper methods for controlling and communicate with Packer, building base images."""
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, NamedTuple

from .vagrant import read_json_file
from ....config_loader import BaseImageSettings, VirtualMachineSettings
from .....utils.helper_methods import (get_config_root, get_data_dir,
                                       get_vm_malvm_package_file)

log = logging.getLogger()

PACKER_PATH = get_data_dir() / "packer"


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


PACKER_FILE_DIR = get_data_dir() / "packer"


class BoxConfiguration(NamedTuple):
    """Basic configuration of VM."""

    packer_template_path: Path
    packer_box_name: str
    vagrant_box_name: str
    username: str
    password: str
    computer_name: str
    language_code: str  # de-DE


def replace_text_in_file(file_path: Path, replacements: Dict[str, str]):
    """Searches and replaces text in a file."""
    with file_path.open("r+") as opened_file:
        text = opened_file.read()
        for searched_text, replacement in replacements.items():
            text = text.replace(searched_text, replacement)
        opened_file.seek(0)
        opened_file.write(text)
        opened_file.truncate()


def edit_last_line_of_text(file: Path, text):
    """Overwrites last line of textfile."""
    with file.open(mode="r+") as opened_file:
        lines = opened_file.readlines()
        lines = lines[:-1]
        lines.append(text)
        opened_file.writelines(lines)


def get_mac_interface_configuration(mac_address: str) -> str:
    if mac_address:
        return f", mac: \"{mac_address.upper().replace(':', '').replace(' - ', '')}\""
    return ""


class PackerTemplate:
    """VM template creation class for Packer."""

    def __init__(self, configuration: BoxConfiguration):
        self.configuration = configuration
        self.name = configuration.packer_template_path.name.split(".")[0]
        self.config_path = get_config_root() / f"data/{self.name}/"
        self.local_packer_template_path = (
                self.config_path / configuration.packer_template_path.name
        )
        self.configured = False

    def configure(self):
        """Configures template with necessary parameters."""
        self.copy_necessary_files()
        self.configure_packer_config()
        self.configure_autounattend_config()
        self.configure_vagrantfile_template()
        self.configured = True

    def configure_autounattend_config(self):
        """Configures Windows Autounattend file."""
        autounattend_config = {
            "insert_username": self.configuration.username,
            "insert_password": self.configuration.password,
            "insert_language_code": self.configuration.language_code,
            "insert_computer_name": self.configuration.computer_name,
        }
        replace_text_in_file(self.get_autounattend_filepath(), autounattend_config)

    def configure_packer_config(self):
        """Configures packers template json file."""
        malvm_package_file_path = str(get_vm_malvm_package_file().absolute())
        malvm_package_file_path = malvm_package_file_path.replace("\\", "/")
        packer_config = {
            "insert_analysevm_path": malvm_package_file_path,
            "insert_username": self.configuration.username,
            "insert_password": self.configuration.password,
        }
        replace_text_in_file(self.local_packer_template_path, packer_config)

    def configure_vagrantfile_template(self):
        """Inserts parameter into Vagrantfile."""
        vagrantfile_template_config = {
            "insert_username": self.configuration.username,
            "insert_password": self.configuration.password
        }
        vagrantfile_template_path = (
                self.config_path / f"vagrantfile-{self.name.lower()}.template"
        )
        replace_text_in_file(vagrantfile_template_path, vagrantfile_template_config)

    def build(self):
        """Builds Vagrant box with Packer.

        Malvm will sanitize the initial box out-of-the-box from
        possible characteristics.
        """
        if not self.configured:
            raise RuntimeError("Box must be configured before build.")
        os.chdir(str(self.config_path.absolute()))
        log.debug(f"Building box {str(self.local_packer_template_path.absolute())}")
        subprocess.run(
            [
                "packer",
                "build",
                "--only=virtualbox-iso",
                "--force",
                str(self.local_packer_template_path.absolute()),
            ],
            check=True,
        )

    def add_to_vagrant(self):
        """Adds box build by Packer to Vagrant environment."""
        log.debug(
            f"Add box {self.configuration.vagrant_box_name} at "
            f"{str(self.config_path / f'{self.name}_virtualbox.box')} to Vagrant")
        subprocess.run(
            [
                "vagrant",
                "box",
                "add",
                self.configuration.vagrant_box_name,
                str(self.config_path / f"{self.name}_virtualbox.box"),
            ],
            check=True,
        )

    def init_vagrantfile(self, vm_name: str, vm_settings: VirtualMachineSettings):
        """Initialize Vagrantfile for Virtual Machine."""
        # virtual_machines = Controller().configuration.virtual_machines
        # vm_settings = virtual_machines.get(vm_name, virtual_machines["default"])
        log.debug(f"Initialize Vagrantfile for {vm_name} with settings {vm_settings}")
        subprocess.run(
            ["vagrant", "init", self.configuration.vagrant_box_name], check=True,
        )
        # TODO if netoworkk .. interface.interface_name does not exist, it needs to be created via vbox
        if vm_settings.network_configuration and vm_settings.network_configuration.interfaces:
            interfaces = "\n".join(
                [
                    f'config.vm.network "private_network", ip: "{interface.ip}"'
                    f'{get_mac_interface_configuration(interface.mac_address)}'
                    for
                    interface in vm_settings.network_configuration.interfaces if interface])
        else:
            interfaces = ""
        modified_vagrantfile_tail = f"""
   # config.vm.network "private_network", ip: "192.168.56.101"
   {interfaces}
   config.disksize.size = "{vm_settings.disk_size}"
   config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = true
    # Customize the amount of memory on the VM:
    vb.memory = "{vm_settings.memory}"
    vb.name = "{vm_name}"
  end
  config.vbguest.auto_update = false
end
        """
        edit_last_line_of_text(Path("Vagrantfile"), modified_vagrantfile_tail)

    def copy_necessary_files(self):
        """Copies all data and configuration files for Packer and Vagrant."""
        files = self.get_necessary_files()
        for file in files:
            Path(self.config_path / file).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(
                str((PACKER_FILE_DIR / file).absolute()),
                str((self.config_path / file).absolute()),
            )

    def get_necessary_files(self) -> List[str]:
        """Returns list of all files, needed to configure the template."""
        with self.configuration.packer_template_path.open() as file_opened:
            text = file_opened.read()
        files = re.findall(r"\"\./(.*)\"", text)
        files_deduplicated = list(set(files))
        files_deduplicated.append(self.configuration.packer_template_path.name)
        return files_deduplicated

    def get_autounattend_filepath(self) -> Path:
        """Returns path of Autounattend.xml."""
        if not self.configuration.packer_template_path.exists():
            raise FileNotFoundError("Packer Template Path was not found.")
        json_text = read_json_file(self.configuration.packer_template_path)
        if "variables" not in json_text or "autounattend" not in json_text["variables"]:
            raise ValueError(
                f"Autounattend file path was not found in "
                f"{self.configuration.packer_template_path.absolute()}. "
                f"Selector: variables -> autounattend"
            )
        autounattend_filepath = json_text["variables"]["autounattend"]
        return Path(self.config_path / autounattend_filepath)
