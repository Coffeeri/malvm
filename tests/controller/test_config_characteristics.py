import pytest
from malvm.controller.config_loader import parse_malvm_yaml_config

from ..conftest import write_configuration

correct_hardening_malvm_config = """
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
    hardening:
      characteristics: CPUID, FVB, MACVB1
"""

hardening_missing_characteristics_malvm_config = """
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
    hardening:
      characteristics:
"""
hardening_missing_characteristics_key_malvm_config = """
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
    hardening:
"""

hardening_missing_hardening_key_malvm_config = """
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
"""


def test_correct_hardening_config(tmp_path):
    yaml_path = write_configuration(tmp_path, correct_hardening_malvm_config)
    loaded_config = parse_malvm_yaml_config(yaml_path)
    assert loaded_config.virtual_machines["fkieVM"].hardening_configuration
    assert loaded_config.virtual_machines["fkieVM"].hardening_configuration.characteristics == ["CPUID", "FVB",
                                                                                                "MACVB1"]


@pytest.mark.parametrize("configuration",
                         [hardening_missing_characteristics_malvm_config, hardening_missing_hardening_key_malvm_config,
                          hardening_missing_characteristics_key_malvm_config])
def test_missing_characteristics_hardening_config(configuration, tmp_path):
    yaml_path = write_configuration(tmp_path, configuration)
    loaded_config = parse_malvm_yaml_config(yaml_path)
    assert loaded_config.virtual_machines["fkieVM"].hardening_configuration is None
