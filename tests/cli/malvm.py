"""This module contains tests for the malvm-cli."""
from click.testing import CliRunner

from malvm.cli.malvm.main import check, controller


def test_check_all(example_characteristic):
    controller.characteristics = {}
    controller.add_characteristic(example_characteristic)
    runner = CliRunner()
    result = runner.invoke(check, [])
    assert result.exit_code == 0


def test_check_specific(example_pre_boot_characteristic):
    controller.characteristics = {}
    controller.add_characteristic(example_pre_boot_characteristic)
    runner = CliRunner()
    result = runner.invoke(check, ["PreBootCharacteristic"])
    assert result.exit_code == 0
    assert str(result.output).startswith("[PREBOOTCHARACTERISTIC] - OK.")


def test_check_not_found(example_pre_boot_characteristic):
    controller.characteristics = {}
    controller.add_characteristic(example_pre_boot_characteristic)
    runner = CliRunner()
    result = runner.invoke(check, ["xyz"])
    assert result.exit_code == 1
    assert result.output == "ERROR: Characteristic was not found.\n"
