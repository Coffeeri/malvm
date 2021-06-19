"""This module test the configuration loading and verification."""
from pathlib import Path

import pytest

from malvm.controller import config_loader
from malvm.controller.config_loader import is_configuration_file_valid, \
    parse_malvm_yaml_config, get_malvm_configuration, TEMPLATE_CONFIG_PATH_SUFFIX_YAML, \
    get_malvm_configuration_file_path, setup_logging, get_logging_config_template, insert_user_conf_in_logging_conf, \
    MisconfigurationException
from malvm.controller.virtual_machine.hypervisor.virtualbox.vagrant import get_vm_names_list, \
    filter_existing_vms_from_config
import malvm.controller.virtual_machine.hypervisor.virtualbox.vagrant as vagrant_helper
from ..conftest import correct_malvm_config, write_configuration

no_default_vm_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
"""
no_vm_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
"""

no_syslog_malvm_config = """
logging:
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
"""

no_rotating_file_path_malvm_config = """
logging:
    syslog_address: /dev/log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
"""

empty_logging_malvm_config = """
logging:
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
"""

no_logging_malvm_config = """
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
"""

no_win10_box_name_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
"""

base_image_mismatch = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-other-image
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
"""

unsupported_template_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: something_wrong
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
"""
correct_network_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      interfaces:
        interface01:
          ip: 192.168.56.101
"""
no_default_gateway_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      interfaces:
        interface01:
          ip: 192.168.56.101
"""
no_interfaces_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
"""
empty_network_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
"""
ip_missing_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      interfaces:
        interface01:
"""
empty_interfaces_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      interfaces:
"""
wrong_gateway_ip_network_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 123
"""
wrong_interface_ip_malvm_config = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      interfaces:
        interface01:
          ip: 123
"""

network_config_with_dns_server = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      dns_server: [1.1.1.1, 8.8.8.8]
      interfaces:
        interface01:
          ip: 192.168.56.101
"""
network_config_with_dns_server_single_string = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      dns_server: 1.1.1.1
      interfaces:
        interface01:
          ip: 192.168.56.101
"""
network_config_with_dns_server_invalid_ip = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      dns_server: abc
      interfaces:
        interface01:
          ip: 192.168.56.101
"""
network_config_with_dns_server_invalid_ips = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      dns_server: [1,2]
      interfaces:
        interface01:
          ip: 192.168.56.101
"""

network_config_with_dns_server_too_many_ips = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      dns_server: [1.1.1.1, 1.0.0.1, 8.8.8.8]
      interfaces:
        interface01:
          ip: 192.168.56.101
"""

network_config_with_mac_address = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      interfaces:
        interface01:
          ip: 192.168.56.101
          mac: 19:6E:68:24:AB:E3
"""
network_config_with_mac_address_dashed = """
logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
base_images:
  malvm-win-10:
    template: windows_10
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
virtual_machines:
  default:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: []
    pip_applications: []
  fkieVM:
    base_image: malvm-win-10
    disk_size: 120GB
    memory: 2048
    choco_applications: [git]
    pip_applications: [black, pytest]
    network:
      default_gateway: 192.168.56.1
      interfaces:
        interface01:
          ip: 192.168.56.101
          mac: 19-6E-68-24-AB-E3
"""


def test_wrong_suffix(tmp_path, caplog):
    path = tmp_path / "test.txt"
    path.touch()
    assert is_configuration_file_valid(path) is False


def test_is_configuration_file_valid(tmp_path):
    config_path = write_configuration(tmp_path, correct_malvm_config)
    assert is_configuration_file_valid(config_path) is True


def test_no_default_vm_defined(tmp_path, caplog):
    config_path = write_configuration(tmp_path, no_default_vm_malvm_config)
    assert is_configuration_file_valid(config_path) is False
    assert "No default Virtual Machine occupancy was found" in caplog.text


def test_no_vm_defined(tmp_path, caplog):
    config_path = write_configuration(tmp_path, no_vm_malvm_config)
    assert is_configuration_file_valid(config_path) is False
    assert "No default Virtual Machine occupancy was found" in caplog.text


def test_no_syslog_defined(tmp_path):
    config_path = write_configuration(tmp_path, no_syslog_malvm_config)
    loaded_config = parse_malvm_yaml_config(config_path)
    assert is_configuration_file_valid(config_path) is True
    assert loaded_config.logging_settings.syslog_address is None
    assert loaded_config.logging_settings.rotating_file_path == Path(
        "~/.local/share/malvm/logs/malvm.log")


def test_no_rotating_file_path_defined(tmp_path):
    config_path = write_configuration(tmp_path, no_rotating_file_path_malvm_config)
    loaded_config = parse_malvm_yaml_config(config_path)
    assert is_configuration_file_valid(config_path) is True
    assert loaded_config.logging_settings.rotating_file_path is None
    assert loaded_config.logging_settings.syslog_address == "/dev/log"


def test_empty_logging_config(tmp_path):
    config_path = write_configuration(tmp_path, empty_logging_malvm_config)
    loaded_config = parse_malvm_yaml_config(config_path)
    assert is_configuration_file_valid(config_path) is True
    assert loaded_config.logging_settings.rotating_file_path is None
    assert loaded_config.logging_settings.syslog_address is None


def test_no_logging_config(tmp_path):
    config_path = write_configuration(tmp_path, no_logging_malvm_config)
    loaded_config = parse_malvm_yaml_config(config_path)
    assert is_configuration_file_valid(config_path) is True
    assert loaded_config.logging_settings.rotating_file_path is None
    assert loaded_config.logging_settings.syslog_address is None


def test_no_base_images(tmp_path, caplog):
    config_path = write_configuration(tmp_path, no_win10_box_name_malvm_config)
    assert is_configuration_file_valid(config_path) is False
    assert "No base image was configured." in caplog.text
    assert "Configuration cannot be loaded." in caplog.text


def test_no_config_found(tmp_path, monkeypatch):
    temp_conf_path = tmp_path / "malvm_config.yaml"
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", temp_conf_path)
    config_exists_pre_execution = temp_conf_path.exists()
    configuration = get_malvm_configuration()
    config_exists_posts_execution = temp_conf_path.exists()
    assert config_exists_pre_execution is False
    assert config_exists_posts_execution is True
    assert configuration == parse_malvm_yaml_config(TEMPLATE_CONFIG_PATH_SUFFIX_YAML)


def test_yml_yaml_failover(tmp_path, monkeypatch):
    yaml_path = tmp_path / "malvm_config.yaml"
    yml_path = tmp_path / "malvm_config.yml"
    yml_path.touch()
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YML", yml_path)
    assert get_malvm_configuration_file_path() == yml_path


def test_yaml_yml_failover(tmp_path, monkeypatch):
    yaml_path = tmp_path / "malvm_config.yaml"
    yml_path = tmp_path / "malvm_config.yml"
    yaml_path.touch()
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YML", yml_path)
    assert get_malvm_configuration_file_path() == yaml_path


def test_base_image_mismatch(tmp_path):
    config_path = write_configuration(tmp_path, base_image_mismatch)
    assert is_configuration_file_valid(config_path) is False


def test_insert_into_logging_conf_no_file(tmp_path, monkeypatch):
    yaml_path = tmp_path / "malvm_config.yaml"
    yml_path = tmp_path / "malvm_config.yml"
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YML", yml_path)
    malvm_conf = get_malvm_configuration()
    logging_conf = insert_user_conf_in_logging_conf(malvm_conf, get_logging_config_template())
    logfile_path_from_file = logging_conf.get("handlers", {}).get("logfile", {}).get("filename", None)
    logfile_path_from_parser = str(malvm_conf.logging_settings.rotating_file_path.expanduser().absolute()) \
        if malvm_conf.logging_settings.rotating_file_path else None

    assert logfile_path_from_file == logfile_path_from_parser
    assert logging_conf.get("handlers", {}).get("syslog", {}).get("address",
                                                                  None) == malvm_conf.logging_settings.syslog_address


def test_insert_user_config_into_logging_config(tmp_path, monkeypatch):
    yaml_path = tmp_path / "malvm_config.yaml"
    yml_path = tmp_path / "malvm_config.yml"
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YML", yml_path)
    malvm_conf = get_malvm_configuration()
    setup_logging(malvm_conf)


def test_insert_user_config_into_logging_config_no_logging(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, no_logging_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    malvm_conf = get_malvm_configuration()
    logging_conf = insert_user_conf_in_logging_conf(malvm_conf, get_logging_config_template())
    assert "syslog" not in logging_conf["handlers"]
    assert "logfile" not in logging_conf["handlers"]


def test_filter_existing_vms_from_config_no_pre_existing_vms(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, correct_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(vagrant_helper, "get_vm_ids_dict", lambda: {})
    malvm_conf = get_malvm_configuration()
    pre_existing_vms = get_vm_names_list()
    filtered_vms = filter_existing_vms_from_config(malvm_conf.virtual_machines)

    assert pre_existing_vms == []
    assert filtered_vms == malvm_conf.virtual_machines


def test_filter_existing_vms_from_config_with_pre_existing_vms(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, correct_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(vagrant_helper, "get_vm_ids_dict", lambda: {"fkieVM": "test_id"})
    malvm_conf = get_malvm_configuration()
    pre_existing_vms = get_vm_names_list()
    filtered_vms = filter_existing_vms_from_config(malvm_conf.virtual_machines)
    malvm_conf.virtual_machines.pop("fkieVM")
    vm_config_with_no_fkieVM = malvm_conf.virtual_machines

    assert pre_existing_vms == ["fkieVM"]
    assert filtered_vms == vm_config_with_no_fkieVM


def test_unsupported_template(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, unsupported_template_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    monkeypatch.setattr(vagrant_helper, "get_vm_ids_dict", lambda: {"fkieVM": "test_id"})
    with pytest.raises(MisconfigurationException):
        get_malvm_configuration()


def test_correct_network_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, correct_network_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    malvm_conf = get_malvm_configuration()
    config = malvm_conf.virtual_machines["fkieVM"]
    assert config.network_configuration is not None
    assert config.network_configuration.default_gateway == "192.168.56.1"
    assert config.network_configuration.interfaces[0].interface_name == "interface01"
    assert config.network_configuration.interfaces[0].ip == "192.168.56.101"


def test_no_gateway_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, no_default_gateway_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    malvm_conf = get_malvm_configuration()
    config = malvm_conf.virtual_machines["fkieVM"]
    assert config.network_configuration is not None
    assert config.network_configuration.default_gateway is None
    assert config.network_configuration.interfaces[0].interface_name == "interface01"
    assert config.network_configuration.interfaces[0].ip == "192.168.56.101"


def test_no_interfaces_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, no_interfaces_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    malvm_conf = get_malvm_configuration()
    config = malvm_conf.virtual_machines["fkieVM"]
    assert config.network_configuration is not None
    assert config.network_configuration.default_gateway == "192.168.56.1"
    assert config.network_configuration.interfaces is None


def test_empty_network_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, empty_network_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    malvm_conf = get_malvm_configuration()
    config = malvm_conf.virtual_machines["fkieVM"]
    assert config.network_configuration is None


def test_ip_missing_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, ip_missing_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    with pytest.raises(MisconfigurationException) as e:
        get_malvm_configuration()
    assert str(e.value) == "IP address of interface interface01 is not configured"


def test_empty_interfaces_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, empty_interfaces_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    malvm_conf = get_malvm_configuration()
    config = malvm_conf.virtual_machines["fkieVM"]
    assert config.network_configuration.interfaces is None


def test_wrong_gateway_ip_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, wrong_gateway_ip_network_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    with pytest.raises(MisconfigurationException) as e:
        get_malvm_configuration()
    assert str(e.value) == "IP address of gateway is not in the correct IPV4 format."


def test_wrong_interface_ip_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, wrong_interface_ip_malvm_config)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    with pytest.raises(MisconfigurationException) as e:
        get_malvm_configuration()
    assert str(e.value) == "IP address of interface interface01 is not in the correct IPV4 format."


def test_dns_server_config(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_dns_server)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    config = get_malvm_configuration()
    assert config.virtual_machines["fkieVM"].network_configuration.dns_server == ["1.1.1.1", "8.8.8.8"]


def test_dns_server_config_single_string(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_dns_server_single_string)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    config = get_malvm_configuration()
    assert config.virtual_machines["fkieVM"].network_configuration.dns_server == ["1.1.1.1", ""]


def test_dns_server_config_invalid_ip(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_dns_server_invalid_ip)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    with pytest.raises(MisconfigurationException) as exc:
        get_malvm_configuration()
    assert str(exc.value) == "Invalid DNS configuration. Invalid IPv4 address."


def test_dns_server_config_invalid_ips(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_dns_server_invalid_ips)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    with pytest.raises(MisconfigurationException) as exc:
        get_malvm_configuration()
    assert str(exc.value) == "Invalid DNS configuration. Invalid IPv4 address."


def test_dns_server_config_too_many_ips(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_dns_server_too_many_ips)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    with pytest.raises(MisconfigurationException) as exc:
        get_malvm_configuration()
    assert str(exc.value) == "Too many DNS servers in configuration. The maximum is 2."


def test_mac_address(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_mac_address)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    config = get_malvm_configuration()
    assert config.virtual_machines["fkieVM"].network_configuration.interfaces[
               0].mac_address == "19:6E:68:24:AB:E3".lower()


def test_mac_address_dashed(tmp_path, monkeypatch):
    yaml_path = write_configuration(tmp_path, network_config_with_mac_address_dashed)
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", yaml_path)
    config = get_malvm_configuration()
    assert config.virtual_machines["fkieVM"].network_configuration.interfaces[
               0].mac_address == "19-6E-68-24-AB-E3".lower()
