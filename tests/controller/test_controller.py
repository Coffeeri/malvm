"""PyTest tests for controller class."""
from typing import Generator

import pytest

from malvm.characteristics.abstract_characteristic import (
    CharacteristicBase,
    LambdaCharacteristic,
    Characteristic,
)
from ..characteristics.test_abstract_characteristic import (
    fixture_test_characteristic,
    fixture_hello_world_lambda,
)
from malvm.controller.controller import Controller


def test_singleton_controller() -> None:
    """Test if Controller Class is a singleton."""
    controller = Controller()
    controller_second = Controller()
    assert controller == controller_second


def test_run_check(
    fixture_test_controller, fixture_test_characteristic, fixture_hello_world_lambda
) -> None:
    """Test if controller runs check."""
    assert fixture_test_controller.get_characteristic_list() == [
        fixture_test_characteristic,
    ]
    assert fixture_test_controller.get_characteristic_list(True) == [
        fixture_test_characteristic,
        fixture_hello_world_lambda,
    ]
    for characteristic, return_value in fixture_test_controller.run_check(
        fixture_hello_world_lambda.slug
    ):

        assert (characteristic, return_value) == fixture_hello_world_lambda.check()


def test_get_characteristic_list_all():
    """Test if all subcharacteristics of characteristics will be returned."""
    controller = Controller()
    characteristics = controller.get_characteristic_list()

    sub_characteristics = [
        sub_characteristic
        for characteristic in characteristics
        for sub_characteristic in characteristic.sub_characteristics.values()
    ]
    found_all_characteristics = controller.get_characteristic_list(True)
    expected_all_characteristics = characteristics.copy()
    expected_all_characteristics.extend(sub_characteristics)
    assert all(
        [found in expected_all_characteristics for found in found_all_characteristics]
    )


def test_value_run_check(fixture_test_controller):
    with pytest.raises(ValueError):
        result_list = [result for result in fixture_test_controller.run_check("ABC")]


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

    assert isinstance(fixture_test_controller.run_checks(), Generator)


@pytest.fixture
def fixture_test_controller(
    fixture_hello_world_lambda, fixture_test_characteristic, monkeypatch
):
    controller: Controller = Controller()
    monkeypatch.setattr(
        controller,
        "characteristics",
        {fixture_test_characteristic.slug: fixture_test_characteristic},
    )
    monkeypatch.setattr(
        controller,
        "characteristics_with_sub_characteristics",
        {
            fixture_test_characteristic.slug: fixture_test_characteristic,
            fixture_hello_world_lambda.slug: fixture_hello_world_lambda,
        },
    )

    return controller


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
