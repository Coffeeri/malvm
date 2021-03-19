"""This module contains methods which load and verify the malvm configuration."""
import logging
import shutil
from logging.config import dictConfig
from pathlib import Path
from typing import NamedTuple, List, Dict, Any, Optional, Tuple

import yaml

from ..cli.utils import print_info
from ..utils.helper_methods import get_data_dir, get_config_root

log = logging.getLogger()


class LoggingSettings(NamedTuple):
    syslog_address: Optional[str]
    rotating_file_path: Optional[Path]


class BaseImageSettings(NamedTuple):
    template: str
    username: str
    password: str
    computer_name: str
    language_code: str


class VirtualMachineSettings(NamedTuple):
    base_image: str
    disk_size: str
    memory: str
    choco_applications: Optional[List[str]]
    pip_applications: Optional[List[str]]


VirtualMachinesType = Dict[str, VirtualMachineSettings]
BaseImagesType = Dict[str, BaseImageSettings]


class MalvmConfigurationSettings(NamedTuple):
    logging_settings: LoggingSettings
    base_images: BaseImagesType
    virtual_machines: VirtualMachinesType


class MisconfigurationException(Exception):
    pass


CONFIG_PATH_SUFFIX_YAML = get_config_root() / "malvm_config.yaml"
CONFIG_PATH_SUFFIX_YML = get_config_root() / "malvm_config.yml"
TEMPLATE_CONFIG_PATH_SUFFIX_YAML = get_data_dir() / "template_malvm_config.yml"


def insert_user_conf_in_logging_conf(malvm_conf: MalvmConfigurationSettings, logging_conf: Dict) -> Dict:
    modified_config = logging_conf.copy()
    if malvm_conf.logging_settings.rotating_file_path:
        rotating_file_path = str(malvm_conf.logging_settings.rotating_file_path.expanduser().absolute())
        modified_config["handlers"]["logfile"]["filename"] = rotating_file_path
    else:
        modified_config["handlers"].pop("logfile")
    if malvm_conf.logging_settings.syslog_address:
        modified_config["handlers"]["syslog"]["address"] = str(malvm_conf.logging_settings.syslog_address)
    else:
        modified_config["handlers"].pop("syslog")
    return modified_config


def setup_logging(malvm_configuration: MalvmConfigurationSettings):
    logging_file_content = get_logging_config_content()
    logging_config = insert_user_conf_in_logging_conf(malvm_configuration, logging_file_content)
    touch_log_file_path(malvm_configuration)
    dictConfig(logging_config)


def touch_log_file_path(malvm_configuration):
    log_file_path = malvm_configuration.logging_settings.rotating_file_path.expanduser()
    if log_file_path:
        log_file_path.parent.mkdir(exist_ok=True, parents=True)
        log_file_path.touch(exist_ok=True)


def get_logging_config_content() -> Dict:
    logging_config_path = get_data_dir() / "logging_config.yml"
    with logging_config_path.open() as read_config:
        logging_config = yaml.full_load(read_config)
    return logging_config


def get_malvm_configuration() -> MalvmConfigurationSettings:
    yaml_config_path = get_malvm_configuration_file_path()
    if not yaml_config_path:
        log.error("No configfile `malvm_config.yml` was found. Default template configuration will be loaded instead.")
        yaml_config_path = load_default_template_configuration()
        print_info(f"Configfile {yaml_config_path.absolute()} was created and loaded.")
    if is_configuration_file_valid(yaml_config_path):
        return parse_malvm_yaml_config(yaml_config_path)
    raise MisconfigurationException("The configuration is wrong configured, please look at the template configuration "
                                    "in the documentation.")


def load_default_template_configuration() -> Path:
    log.debug(f"Copy configuration {TEMPLATE_CONFIG_PATH_SUFFIX_YAML} to {CONFIG_PATH_SUFFIX_YAML}")
    shutil.copy(TEMPLATE_CONFIG_PATH_SUFFIX_YAML, CONFIG_PATH_SUFFIX_YAML)
    return CONFIG_PATH_SUFFIX_YAML


def get_malvm_configuration_file_path() -> Optional[Path]:
    if CONFIG_PATH_SUFFIX_YAML.exists():
        return CONFIG_PATH_SUFFIX_YAML
    if CONFIG_PATH_SUFFIX_YML.exists():
        return CONFIG_PATH_SUFFIX_YML
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
        log.error(f"No default Virtual Machine occupancy was found in configuration.\n"
                  f"File {yaml_path.absolute()}")
        return False
    return True


def parse_malvm_yaml_config(yaml_path: Path) -> MalvmConfigurationSettings:
    loaded_configuration = get_json_from_yaml_file(yaml_path)
    base_image_settings_dict, logging_settings_dict, vm_settings_dict = fetch_settings_dict_or_none(
        loaded_configuration)

    base_images_settings_dict = parse_base_images_settings(base_image_settings_dict)
    logging_settings_object = parse_logging_settings(logging_settings_dict)
    virtual_machines_setting_dict = parse_vm_settings(vm_settings_dict)

    check_base_image_mismatch(base_images_settings_dict, virtual_machines_setting_dict)
    malvm_configuration = MalvmConfigurationSettings(
        logging_settings=logging_settings_object,
        base_images=base_images_settings_dict,
        virtual_machines=virtual_machines_setting_dict
    )
    log.debug(f"Parsed malvm config {malvm_configuration}")
    return malvm_configuration


def check_base_image_mismatch(base_images_settings_dict, virtual_machines_setting_dict):
    found_base_images = set(base_images_settings_dict.keys())
    found_vm_used_base_images = {vm.base_image for vm in virtual_machines_setting_dict.values()}
    if not found_vm_used_base_images.issubset(found_base_images):
        raise KeyError("The base images do not match the ones, used in Virtual Machine settings.")


def fetch_settings_dict_or_none(loaded_configuration) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    logging_settings_dict = loaded_configuration["logging"] if "logging" in loaded_configuration else None
    base_image_settings_dict = loaded_configuration["base_images"] if "base_images" in loaded_configuration else None
    vm_settings_dict = loaded_configuration["virtual_machines"] if "virtual_machines" in loaded_configuration else None
    return base_image_settings_dict, logging_settings_dict, vm_settings_dict


def parse_logging_settings(logging_settings_dict: Optional[Dict]) -> LoggingSettings:
    if not logging_settings_dict:
        return LoggingSettings(None, None)
    syslog_address = logging_settings_dict["syslog_address"] \
        if "syslog_address" in logging_settings_dict else None
    rotating_file_path = Path(logging_settings_dict["rotating_file_path"]) \
        if "rotating_file_path" in logging_settings_dict else None
    return LoggingSettings(syslog_address=syslog_address, rotating_file_path=rotating_file_path)


def parse_base_images_settings(base_image_settings_dict: Optional[Dict]) -> BaseImagesType:
    if not base_image_settings_dict:
        log.exception("No base image was configured.")
        raise KeyError("No base image was configured.")
    base_images_dict = {base_image_name: BaseImageSettings(
        template=str(base_image["template"]),
        username=str(base_image["username"]),
        password=str(base_image["password"]),
        computer_name=str(base_image["computer_name"]),
        language_code=str(base_image["language_code"]),
    ) for base_image_name, base_image in base_image_settings_dict.items()}

    for base_image in base_images_dict.values():
        if base_image.template != "windows_10":
            raise KeyError("Only Templates: windows_10 are supported at the moment.")
    return base_images_dict


def parse_vm_settings(vm_settings_dict: Optional[Dict]) -> VirtualMachinesType:
    if not vm_settings_dict:
        return {}
    virtual_machines_setting_dict = {
        vm_name: VirtualMachineSettings(
            base_image=vm_setting["base_image"],
            disk_size=vm_setting["disk_size"],
            memory=vm_setting["memory"],
            choco_applications=vm_setting["choco_applications"],
            pip_applications=vm_setting["pip_applications"]
        ) for vm_name, vm_setting in
        vm_settings_dict.items()
    }
    return virtual_machines_setting_dict
