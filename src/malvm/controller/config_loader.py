"""This module contains methods which load and verify the malvm configuration."""
import logging
import shutil
import sys
from logging.config import dictConfig
from pathlib import Path
from typing import NamedTuple, List, Dict, Any, Optional

import yaml

from malvm.cli.utils import print_info
from malvm.utils.helper_methods import get_data_dir, get_config_root

log = logging.getLogger()


class LoggingSettings(NamedTuple):
    syslog_address: Optional[str]
    rotating_file_path: Optional[Path]


class VirtualMachineSettings(NamedTuple):
    username: str
    password: str
    computer_name: str
    language_code: str
    windows_box: str
    disk_size: str
    memory: str
    choco_applications: Optional[List[str]]
    pip_applications: Optional[List[str]]


VirtualMachinesType = Dict[str, VirtualMachineSettings]


class MalvmConfigurationSettings(NamedTuple):
    win10_vagrant_box_name: str
    logging_settings: LoggingSettings
    virtual_machines: VirtualMachinesType


CONFIG_PATH_SUFFIX_YAML = get_config_root() / "malvm_config.yaml"
CONFIG_PATH_SUFFIX_YML = get_config_root() / "malvm_config.yml"
TEMPLATE_CONFIG_PATH_SUFFIX_YAML = get_data_dir() / "template_malvm_config.yml"


def setup_logging():
    with (get_data_dir() / "logging_config.yml").open() as read_config:
        config = yaml.load(read_config, Loader=yaml.FullLoader)
    dictConfig(config)


def get_malvm_configuration() -> MalvmConfigurationSettings:
    yaml_config_path = get_malvm_configuration_file_path()
    if not yaml_config_path:
        log.error("No configfile `malvm_config.yml` was found. Default template configuration will be loaded instead.")
        yaml_config_path = load_default_template_configuration()
        print_info(f"Configfile {yaml_config_path.absolute()} was created and loaded.")
    return parse_malvm_yaml_config(yaml_config_path)


def load_default_template_configuration() -> Path:
    log.debug(f"Copy configuration {TEMPLATE_CONFIG_PATH_SUFFIX_YAML} to {CONFIG_PATH_SUFFIX_YAML}")
    shutil.copy(TEMPLATE_CONFIG_PATH_SUFFIX_YAML, CONFIG_PATH_SUFFIX_YAML)
    return CONFIG_PATH_SUFFIX_YAML


def get_malvm_configuration_file_path() -> Optional[Path]:
    if CONFIG_PATH_SUFFIX_YAML.exists():
        return CONFIG_PATH_SUFFIX_YAML
    elif CONFIG_PATH_SUFFIX_YML.exists():
        return CONFIG_PATH_SUFFIX_YML
    else:
        return None


def get_json_from_yaml_file(yaml_path: Path) -> Dict[str, Any]:
    with yaml_path.open() as opened_file:
        loaded_configuration = yaml.full_load(opened_file)
    return loaded_configuration


def is_configuration_file_valid(yaml_path: Path) -> bool:
    if not yaml_path.suffix.endswith((".yaml", ".yml")):
        return False
    try:
        malvm_config = parse_malvm_yaml_config(yaml_path)
    except (KeyError, TypeError):
        log.exception("Configuration cannot be loaded.")
        return False
    if "default" not in malvm_config.virtual_machines:
        log.error(f"No default virtual machine occupancy was found in configuration.\n"
                  f"File {yaml_path.absolute()}")
        return False
    return True


def parse_malvm_yaml_config(yaml_path: Path) -> MalvmConfigurationSettings:
    loaded_configuration = get_json_from_yaml_file(yaml_path)
    settings_dict = loaded_configuration["settings"]
    vm_settings_dict = loaded_configuration["virtual_machines"]
    logging_settings_dict = settings_dict["logging"] if "logging" in settings_dict else None

    win10_vagrant_box_name = settings_dict["win10_vagrant_box_name"] \
        if "win10_vagrant_box_name" in settings_dict else "malvm-win-10"
    logging_settings_object = parse_logging_settings(logging_settings_dict)
    virtual_machines_setting_dict = parse_vm_settings(vm_settings_dict)

    malvm_configuration = MalvmConfigurationSettings(
        win10_vagrant_box_name=win10_vagrant_box_name,
        logging_settings=logging_settings_object,
        virtual_machines=virtual_machines_setting_dict
    )
    log.debug(f"Parsed malvm config {malvm_configuration}")
    return malvm_configuration


def parse_logging_settings(logging_settings_dict: Optional[Dict]) -> LoggingSettings:
    if not logging_settings_dict:
        return LoggingSettings(None, None)
    syslog_address = logging_settings_dict["syslog_address"] \
        if "syslog_address" in logging_settings_dict else None
    rotating_file_path = Path(logging_settings_dict["rotating_file_path"]) \
        if "rotating_file_path" in logging_settings_dict else None
    return LoggingSettings(syslog_address=syslog_address, rotating_file_path=rotating_file_path)


def parse_vm_settings(vm_settings_dict: Optional[Dict]) -> VirtualMachinesType:
    if not vm_settings_dict:
        return {}
    virtual_machines_setting_dict = {
        vm_name: VirtualMachineSettings(
            username=vm_setting["username"],
            password=vm_setting["password"],
            computer_name=vm_setting["computer_name"],
            language_code=vm_setting["language_code"],
            windows_box=vm_setting["windows_box"],
            disk_size=vm_setting["disk_size"],
            memory=vm_setting["memory"],
            choco_applications=vm_setting["choco_applications"],
            pip_applications=vm_setting["pip_applications"]
        ) for vm_name, vm_setting in
        vm_settings_dict.items()
    }
    return virtual_machines_setting_dict
