"""This module contains fixtures for tests on a global level."""
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


@pytest.fixture
def example_controller(example_characteristic) -> Controller:
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
