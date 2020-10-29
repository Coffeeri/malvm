"""PyTest tests for controller class."""
from typing import Generator

import pytest

from malvm.characteristics.abstract_characteristic import (
    LambdaCharacteristic,
    Characteristic,
    Runtime,
)

from malvm.controller.controller import Controller, load_characteristics_by_path


def test_singleton_controller(example_controller):
    controller_second = Controller()
    assert example_controller == controller_second


def test_add_characteristic(example_controller, example_characteristic):
    expected = {
        example_characteristic.slug: example_characteristic,
        **example_controller.characteristics,
    }
    example_controller.add_characteristic(example_characteristic)
    actual = example_controller.characteristics
    assert expected == actual


def test_characteristic_loaded(example_controller, example_characteristic):
    characteristics = list(
        load_characteristics_by_path(example_controller.characteristics_path)
    )
    expected_list = sorted(
        characteristics + [example_characteristic], key=lambda c: c.slug
    )
    actual_list = sorted(
        example_controller.get_characteristic_list(False, Runtime.DEFAULT)
        + example_controller.get_characteristic_list(False, Runtime.PRE_BOOT),
        key=lambda c: c.slug,
    )

    assert len(expected_list) == len(actual_list)
    assert all(a == b for a, b in zip(expected_list, actual_list))


def test_sub_characteristics_included(example_controller):
    characteristics = list(
        load_characteristics_by_path(example_controller.characteristics_path)
    )
    expected_sub_characteristics = []
    for characteristic in characteristics:
        expected_sub_characteristics.append(characteristic)
        expected_sub_characteristics.extend(characteristic.sub_characteristics.values())

    expected_sub_characteristics = sorted(
        expected_sub_characteristics, key=lambda c: c.slug
    )
    actual_sub_characteristics = sorted(
        example_controller.get_characteristic_list(True, Runtime.DEFAULT)
        + example_controller.get_characteristic_list(True, Runtime.PRE_BOOT),
        key=lambda c: c.slug,
    )
    assert len(expected_sub_characteristics) == len(actual_sub_characteristics)
    assert expected_sub_characteristics == actual_sub_characteristics


def test_run_check(example_controller, example_lambda_sub_characteristic) -> None:
    expected_characteristics = example_controller.get_characteristic_list()
    actual_characteristic = Characteristic("TEST", "Test characteristic")
    actual_characteristic.add_sub_characteristic(example_lambda_sub_characteristic)

    assert len(example_controller.get_characteristic_list()) == 1
    assert expected_characteristics[0] == actual_characteristic

    assert example_controller.get_characteristic_list(True) == [
        actual_characteristic,
        example_lambda_sub_characteristic,
    ]
    for characteristic, return_value in example_controller.get_check_results(
        example_lambda_sub_characteristic.slug
    ):

        assert (
            characteristic,
            return_value,
        ) == example_lambda_sub_characteristic.check()


def test_value_run_check(fixture_test_controller):
    with pytest.raises(ValueError):
        result_list = [
            result for result in fixture_test_controller.get_check_results("ABC")
        ]


def test_nested_characteristics_run_check(
    fixture_test_controller, fixture_sub_characteristic_multi
):
    fixture_test_controller.characteristics[
        fixture_sub_characteristic_multi.slug
    ] = fixture_sub_characteristic_multi
    fixture_test_controller.characteristics_with_sub_characteristics[
        fixture_sub_characteristic_multi.slug
    ] = fixture_sub_characteristic_multi
    fixture_test_controller.characteristics_with_sub_characteristics[
        list(fixture_sub_characteristic_multi.sub_characteristics.values())[0].slug
    ] = list(fixture_sub_characteristic_multi.sub_characteristics.values())[0]

    assert isinstance(fixture_test_controller.get_all_checks_results(), Generator)


@pytest.fixture
def fixture_sub_characteristic_multi() -> Characteristic:
    characteristic = Characteristic("SRC001", "Single Return Characteristic")
    characteristic.add_sub_characteristic(
        LambdaCharacteristic(
            "SRC002",
            "Single Return Characteristic 2",
            "",
            lambda x: False,
            lambda x: True,
        )
    )
    return characteristic


@pytest.fixture
def example_controller(example_characteristic) -> Controller:
    controller = Controller()
    controller.add_characteristic(example_characteristic)
    return controller


@pytest.fixture
def example_characteristic(example_lambda_sub_characteristic):
    characteristic = Characteristic("TEST", "Test characteristic")
    characteristic.add_sub_characteristic(example_lambda_sub_characteristic)
    return characteristic


@pytest.fixture
def example_lambda_sub_characteristic() -> LambdaCharacteristic:
    """Fixture with hello world function."""
    return LambdaCharacteristic(
        "HWORLD",
        "This is an example LambdaCharacteristic.",
        "Hello world.",
        lambda x: True,
        lambda x: False,
    )
