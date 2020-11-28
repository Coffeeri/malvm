"""Module containing a generic template with configuration for virtual machines."""
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, NamedTuple

import click
from ..malvm.utils import print_result

from ...controller.controller import Controller
from ...utils.helper_methods import (
    get_config_root,
    get_data_dir,
    get_vm_malvm_package_file,
    read_json_file,
)

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


class PackerTemplate:
    """VM template creation class for Packer."""

    def __init__(self, name: str, configuration: BoxConfiguration):
        self.name = name
        self.configuration = configuration
        self.config_path = get_config_root() / f"data/{self.name}/"
        self.local_packer_template_path = (
            self.config_path / self.configuration.packer_template_path.name
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
            "insert_password": self.configuration.password,
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
        subprocess.run(
            [
                "packer",
                "build",
                "--only=virtualbox-iso",
                str(self.local_packer_template_path.absolute()),
            ],
            check=True,
        )

    def add_to_vagrant(self):
        """Adds box build by Packer to Vagrant environment."""
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

    def init_vagrantfile(self, vm_name: str):
        """Initialize Vagrantfile for virtual machine."""
        subprocess.run(
            ["vagrant", "init", self.configuration.vagrant_box_name], check=True,
        )

        ignore_vbguest_additions = f"""
   config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = true
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
    vb.name = "{vm_name}"
  end
  config.vbguest.auto_update = false
end
        """
        edit_last_line_of_text(Path("Vagrantfile"), ignore_vbguest_additions)

    def setup_virtualmachine(self, vm_name: str, vagrantfile_output: Path = Path.cwd()):
        """Setup and start virtual machine with vagrant.

        This method initializes the Vagrantfile, starts the virtual machine,
        fixes all characteristics and saves a snapshot of the clean state.
        """
        os.chdir(
            str(vagrantfile_output.absolute())
            if vagrantfile_output.is_dir()
            else str(vagrantfile_output.parent.absolute())
        )
        self.init_vagrantfile(vm_name)
        subprocess.run(
            ["vagrant", "up"], check=True,
        )
        subprocess.run(
            ["vagrant", "halt"], check=True,
        )
        run_pre_boot_fixes(vm_name)
        subprocess.run(
            ["vagrant", "up"], check=True,
        )
        subprocess.run(
            ["vagrant", "winrm", "-e", "-c", "malvm fix"], check=True,
        )
        subprocess.run(
            ["vagrant", "snapshot", "save", "clean-state"], check=True,
        )

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


def run_pre_boot_fixes(vm_name: str):
    """Runs fixes of characteristics with RUNTIME PRE_BOOT.

    Args:
        vm_name (str): Name of virtual machine in VirtualBox.
    """
    controller: Controller = Controller()
    click.echo(
        click.style("> Checking and fixing pre boot characteristics...", fg="yellow",)
    )
    environment = {"os": platform.system(), "vm_name": vm_name}
    for characteristic, return_status in controller.apply_pre_boot_fixes(environment):
        print_result(characteristic, return_status)
