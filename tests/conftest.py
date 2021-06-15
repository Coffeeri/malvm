"""This module contains fixtures for tests on a global level."""
from pathlib import Path

import pytest

from malvm.characteristics.abstract_characteristic import (
    LambdaCharacteristic,
    Characteristic,
    CharacteristicAttributes,
    Runtime,
    CheckResult,
    CheckType,
)
from malvm.controller.controller import Controller
from malvm.controller.virtual_machine.vm_manager import VirtualMachineManager

correct_malvm_config = """
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


@pytest.fixture
def example_vm_manager():
    return VirtualMachineManager()


@pytest.fixture
def example_controller(example_characteristic) -> Controller:
    controller = Controller()
    controller.add_characteristic(example_characteristic)
    return controller


@pytest.fixture
def example_controller_good_config(tmp_path, example_characteristic) -> Controller:
    write_configuration(tmp_path, correct_malvm_config)
    controller = Controller()
    controller.add_characteristic(example_characteristic)
    return controller


@pytest.fixture
def example_characteristic(example_lambda_sub_characteristic):
    class TestCharacteristic(Characteristic):
        def __init__(self, slug, description):
            super().__init__(slug, description)

    characteristic = TestCharacteristic("TEST", "Test characteristic")
    characteristic.add_sub_characteristic(example_lambda_sub_characteristic)
    return characteristic


@pytest.fixture
def example_lambda_sub_characteristic() -> LambdaCharacteristic:
    """Fixture with hello world function."""
    return LambdaCharacteristic(
        slug="HWORLD",
        description="This is an example LambdaCharacteristic.",
        value="Hello world.",
        check_func=lambda x: True,
        fix_func=lambda x: False,
    )


@pytest.fixture()
def example_pre_boot_characteristic():
    class PreBootCharacteristic(Characteristic):
        """Checks and Fixes cpuid hypervisor bit in Virtualbox."""

        def __init__(self):
            super().__init__(
                "PreBootCharacteristic",
                "Example pre boot characteristic.",
                CharacteristicAttributes(runtime=Runtime.PRE_BOOT),
            )

        def check(self) -> CheckResult:
            yield self, CheckType(str(self.environment), True)

        def fix(self) -> CheckResult:
            yield self, CheckType(str(self.environment), False)

    return PreBootCharacteristic()


def write_configuration(temp_dir: Path, config: str) -> Path:
    config_path = temp_dir / "malvm_configuration.yml"
    with config_path.open("w") as opened_file:
        opened_file.write(config)
    return config_path
