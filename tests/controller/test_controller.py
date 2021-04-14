"""PyTest tests for controller class."""

import pytest

from malvm.characteristics.abstract_characteristic import (
    Runtime,
    CheckType,
)
from malvm.controller.controller import (
    Controller,
    load_characteristics_by_path,
)


def test_singleton_controller(example_controller):
    controller_second = Controller()
    assert example_controller == controller_second


def test_add_characteristic(
        example_controller, example_characteristic,
):
    expected = {
        example_characteristic.slug: example_characteristic,
        **example_controller.characteristics,
    }

    example_controller.add_characteristic(example_characteristic)

    assert expected == example_controller.characteristics


def test_characteristic_loaded(
        example_controller, example_characteristic,
):
    characteristics = (
        *load_characteristics_by_path(example_controller.characteristics_path),
        example_characteristic,
    )
    expected_list = sorted(characteristics, key=lambda c: c.slug, )

    actual_list = sorted(
        example_controller.get_characteristic_list(False, Runtime.DEFAULT, )
        + example_controller.get_characteristic_list(False, Runtime.PRE_BOOT, ),
        key=lambda c: c.slug,
    )

    assert expected_list == actual_list


def test_sub_characteristics_included(
        example_controller, example_characteristic,
):
    characteristics = list(
        load_characteristics_by_path(example_controller.characteristics_path)
    ) + [example_characteristic]
    expected_sub_characteristics = []
    for characteristic in characteristics:
        expected_sub_characteristics.append(characteristic)
        expected_sub_characteristics.extend(characteristic.sub_characteristics.values())

    expected_sub_characteristics = sorted(
        expected_sub_characteristics, key=lambda c: c.slug,
    )
    actual_sub_characteristics = sorted(
        example_controller.get_characteristic_list(True, Runtime.DEFAULT, )
        + example_controller.get_characteristic_list(True, Runtime.PRE_BOOT, ),
        key=lambda c: c.slug,
    )
    assert expected_sub_characteristics == actual_sub_characteristics


def test_get_checks_results(example_controller, example_characteristic):
    example_controller.characteristics = {}
    example_controller.add_characteristic(example_characteristic)
    actual_characteristics = example_controller.get_characteristic_list(
        True, Runtime.DEFAULT
    )

    actual_results = [*example_controller.get_all_checks_results()]
    expected_results = [*example_characteristic.check()]

    assert actual_characteristics == [
        example_characteristic,
        *example_characteristic.sub_characteristics.values(),
    ]
    assert actual_results == expected_results


def test_apply_all_fixes_get_results(example_controller, example_characteristic):
    example_controller.characteristics = {}
    example_controller.add_characteristic(example_characteristic)

    actual_results = [*example_controller.apply_all_fixes_get_results()]
    expected_results = [*example_characteristic.fix()]

    assert actual_results == expected_results
    for _, (_, returned_status) in actual_results:
        assert not returned_status


def test_pre_boot_check(example_controller, example_pre_boot_characteristic):
    example_controller.characteristics = {}
    example_controller.add_characteristic(example_pre_boot_characteristic)
    example_env = {"test_env": "test"}
    actual_post_boot_list = example_controller.get_characteristic_list(
        True, Runtime.DEFAULT
    )

    actual_check_results = [
        *example_controller.get_pre_boot_checks_results(example_env)
    ]
    expected_check_result = (
        example_pre_boot_characteristic,
        CheckType(str(example_env), True),
    )

    assert actual_check_results == [expected_check_result]
    assert actual_post_boot_list == []


def test_pre_boot_fix(example_controller, example_pre_boot_characteristic):
    example_controller.characteristics = {}
    example_controller.add_characteristic(example_pre_boot_characteristic)
    example_env = {"test_env": "test"}
    actual_post_boot_list = example_controller.get_characteristic_list(
        True, Runtime.DEFAULT
    )

    actual_check_results = [*example_controller.apply_pre_boot_fixes(example_env)]
    expected_check_result = (
        example_pre_boot_characteristic,
        CheckType(str(example_env), False),
    )

    assert actual_check_results == [expected_check_result]
    assert actual_post_boot_list == []


def test_get_characteristic_list(example_controller, example_characteristic):
    example_controller.characteristics = {}
    example_controller.add_characteristic(example_characteristic)
    expected_characteristics = [example_characteristic]
    expected_characteristics_with_sub = [
        example_characteristic,
        *example_characteristic.sub_characteristics.values(),
    ]
    actual_characteristics = example_controller.get_characteristic_list(False)
    actual_characteristics_with_sub = example_controller.get_characteristic_list(True)

    assert expected_characteristics == actual_characteristics
    assert expected_characteristics_with_sub == actual_characteristics_with_sub


def test_check_unknown_characteristic(example_controller):
    with pytest.raises(ValueError):
        [*example_controller.get_check_results("random_slug")]