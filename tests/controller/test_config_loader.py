"""This module test the configuration loading and verification."""
from pathlib import Path

from malvm.controller import config_loader
from malvm.controller.config_loader import is_configuration_file_valid, \
    parse_malvm_yaml_config, get_malvm_configuration, get_malvm_configuration_file_path, \
    TEMPLATE_CONFIG_PATH_SUFFIX_YAML
from malvm.utils.helper_methods import get_data_dir

correct_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
  logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
virtual_machines:
  default:
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 2048MB
    choco_applications: [git]
    pip_applications: []
  fkieVM:
    username: peter
    password: 654321
    computer_name: PC
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 4096MB
    choco_applications: [git]
    pip_applications: []
"""

no_default_vm_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
  logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
virtual_machines:
  fkieVM:
    username: peter
    password: 654321
    computer_name: PC
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 4096MB
    choco_applications: [git]
    pip_applications: []
"""
no_vm_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
  logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
virtual_machines:
"""

no_syslog_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
  logging:
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
virtual_machines:
  default:
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 2048MB
    choco_applications: [git]
    pip_applications: []
"""

no_rotating_file_path_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
  logging:
    syslog_address: /dev/log
virtual_machines:
  default:
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 2048MB
    choco_applications: [git]
    pip_applications: []
"""

empty_logging_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
  logging:
virtual_machines:
  default:
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 2048MB
    choco_applications: [git]
    pip_applications: []
"""

no_logging_malvm_config = """
settings:
  win10_vagrant_box_name: malvm-win-10
virtual_machines:
  default:
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 2048MB
    choco_applications: [git]
    pip_applications: []
"""

no_win10_box_name_malvm_config = """
settings:
  logging:
    syslog_address: /dev/log
    rotating_file_path: ~/.local/share/malvm/logs/malvm.log
virtual_machines:
  default:
    username: max
    password: 123456
    computer_name: Computer
    language_code: de-De
    windows_box: malvm-win-10
    disk_size: 120GB
    memory: 2048MB
    choco_applications: [git]
    pip_applications: []
"""


def test_wrong_suffix(tmp_path, caplog):
    path = tmp_path / "test.txt"
    path.touch()
    assert is_configuration_file_valid(path) is False


def write_configuration(temp_dir: Path, config: str) -> Path:
    config_path = temp_dir / "malvm_configuration.yml"
    with config_path.open("w") as opened_file:
        opened_file.write(config)
    return config_path


def test_is_configuration_file_valid(tmp_path):
    config_path = write_configuration(tmp_path, correct_malvm_config)
    assert is_configuration_file_valid(config_path) is True


def test_no_default_vm_defined(tmp_path, caplog):
    config_path = write_configuration(tmp_path, no_default_vm_malvm_config)
    assert is_configuration_file_valid(config_path) is False
    assert "No default virtual machine occupancy was found" in caplog.text


def test_no_vm_defined(tmp_path, caplog):
    config_path = write_configuration(tmp_path, no_vm_malvm_config)
    assert is_configuration_file_valid(config_path) is False
    assert "No default virtual machine occupancy was found" in caplog.text


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


def test_no_win10_vagrant_box_name(tmp_path):
    config_path = write_configuration(tmp_path, no_win10_box_name_malvm_config)
    loaded_config = parse_malvm_yaml_config(config_path)
    assert is_configuration_file_valid(config_path) is True
    assert loaded_config.win10_vagrant_box_name == "malvm-win-10"


def test_no_yaml_found(tmp_path, monkeypatch):
    temp_conf_path = tmp_path / "malvm_config.yaml"
    monkeypatch.setattr(config_loader, "CONFIG_PATH_SUFFIX_YAML", temp_conf_path)
    config_exists_pre_execution = temp_conf_path.exists()
    configuration = get_malvm_configuration()
    config_exists_posts_execution = temp_conf_path.exists()
    assert config_exists_pre_execution is False
    assert config_exists_posts_execution is True
    assert configuration == parse_malvm_yaml_config(TEMPLATE_CONFIG_PATH_SUFFIX_YAML)
