"""Module containing a generic template with configuration for virtual machines."""
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple, List, Dict

from malvm.utils.helper_methods import (
    get_config_root,
    get_data_dir,
    read_json_file,
    get_vm_malvm_egg,
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
    with file_path.open("r+") as opened_file:
        text = opened_file.read()
        for searched_text, replacement in replacements.items():
            text = text.replace(searched_text, replacement)
        opened_file.seek(0)
        opened_file.write(text)
        opened_file.truncate()


def edit_last_line_of_text(file: Path, text):
    with file.open(mode="r+") as opened_file:
        lines = opened_file.readlines()
        lines = lines[:-1]
        lines.append(text)
        opened_file.writelines(lines)


class PackerTemplate:
    def __init__(self, name: str, configuration: BoxConfiguration):
        self.name = name
        self.configuration = configuration
        self.config_path = get_config_root() / f"data/{self.name}/"
        self.LOCAL_PACKER_TEMPLATE_PATH = (
            self.config_path / self.configuration.packer_template_path.name
        )
        self.configured = False

    def configure(self):
        self.copy_necessary_files()
        self.configure_packer_config()
        self.configure_autounattend_config()
        self.configure_vagrantfile_template()
        self.configured = True

    def configure_autounattend_config(self):
        AUTOUNATTEND_CONFIG = {
            "insert_username": self.configuration.username,
            "insert_password": self.configuration.password,
            "insert_language_code": self.configuration.language_code,
            "insert_computer_name": self.configuration.computer_name,
        }
        replace_text_in_file(self.get_autounattend_filepath(), AUTOUNATTEND_CONFIG)

    def configure_packer_config(self):
        PACKER_CONFIG = {
            "insert_analysevm_path": str(get_vm_malvm_egg().absolute()),
            "insert_username": self.configuration.username,
            "insert_password": self.configuration.password,
        }
        replace_text_in_file(self.LOCAL_PACKER_TEMPLATE_PATH, PACKER_CONFIG)

    def configure_vagrantfile_template(self):
        VAGRANTFILE_TEMPLATE_CONFIG = {
            "insert_username": self.configuration.username,
            "insert_password": self.configuration.password,
        }
        vagrantfile_template_path = (
            self.config_path / f"vagrantfile-{self.name.lower()}.template"
        )
        replace_text_in_file(vagrantfile_template_path, VAGRANTFILE_TEMPLATE_CONFIG)

    def build(self):
        if not self.configured:
            raise RuntimeError("Box must be configured before build.")
        os.chdir(str(self.config_path.absolute()))
        subprocess.run(
            [
                "packer",
                "build",
                "--only=virtualbox-iso",
                str(self.LOCAL_PACKER_TEMPLATE_PATH.absolute()),
            ],
            check=True,
        )

    def add_to_vagrant(self):
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
            ["vagrant", "winrm", "-e", "-c", "malvm fix"], check=True,
        )
        subprocess.run(
            ["vagrant", "snapshot", "save", "clean-state"], check=True,
        )

    def copy_necessary_files(self):
        files_deduplicated = self.get_necessary_files()
        for file in files_deduplicated:
            Path(self.config_path / file).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(
                str((PACKER_FILE_DIR / file).absolute()),
                str((self.config_path / file).absolute()),
            )

    def get_necessary_files(self) -> List[str]:
        with self.configuration.packer_template_path.open() as file_opened:
            text = file_opened.read()
        files = re.findall(r"\"\./(.*)\"", text)
        files_deduplicated = list(set(files))
        files_deduplicated.append(self.configuration.packer_template_path.name)
        return files_deduplicated

    def get_autounattend_filepath(self) -> Path:
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
