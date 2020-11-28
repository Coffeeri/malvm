"""PyTest tests for Characteristic class."""
import platform
from typing import List, Tuple

import pytest

from malvm.characteristics.abstract_characteristic import (
    Characteristic,
    LambdaCharacteristic,
    CheckType,
    CharacteristicBase,
)


@pytest.mark.parametrize(
    "slug, description", [("TEST", "This characteristic checks is just an example.")],
)
def test_characteristic_attribute(slug, description) -> None:
    """Test if slug and description are set correctly."""
    characteristic = Characteristic(slug, description)
    assert characteristic.slug == slug
    assert characteristic.description == description


@pytest.mark.parametrize(
    "slug, description, value, check_func, fix_func, expected_return_check, "
    "expected_return_fix",
    [
        (
            "TEST",
            "This characteristic checks is just an example.",
            "Hello world",
            lambda x: False,
            lambda x: f"{x} all!",
            False,
            "Hello world all!",
        )
    ],
)
def test_lambda_characteristic_basic(
    slug,
    description,
    value,
    check_func,
    fix_func,
    expected_return_check,
    expected_return_fix,
) -> None:
    """Test if LambdaCharacteristic can be initiated with a hello world func."""
    lambda_characteristic = LambdaCharacteristic(
        slug, description, value, check_func, fix_func
    )
    assert lambda_characteristic.slug == slug
    assert lambda_characteristic.description == description
    assert lambda_characteristic.check() == CheckType(
        description, expected_return_check
    )
    assert lambda_characteristic.fix() == CheckType(description, expected_return_fix)


def test_combine_characteristic_lambda(
    example_characteristic, example_lambda_sub_characteristic
) -> None:
    test_characteristic = example_characteristic
    assert test_characteristic.slug == "TEST"
    assert test_characteristic.description == "Test characteristic"
    assert test_characteristic.sub_characteristics == {
        example_lambda_sub_characteristic.slug: example_lambda_sub_characteristic
    }
    result_list: List[Tuple[CharacteristicBase, CheckType]] = []
    for result in test_characteristic.check():
        result_list.append(result)
    characteristic, result = result_list[0]
    if platform.system() != "Windows":
        assert characteristic.slug == example_characteristic.slug
        assert characteristic.description == example_characteristic.description
        assert result.check_value == "Skipped, malvm is not running on Windows."
        assert not result.check_status
