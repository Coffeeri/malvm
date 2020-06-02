"""PyTest tests for Characteristic class."""
from typing import List

import pytest

from malvm.characteristics.abstract_characteristic import (
    Characteristic,
    LambdaCharacteristic,
    CheckType,
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
            lambda x: (x, False),
            lambda x: f"{x} all!",
            ("Hello world", False),
            ("Hello world", False),
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
    assert lambda_characteristic.check() == expected_return_check
    assert lambda_characteristic.fix() == expected_return_fix


def test_combine_characteristic_lambda(
    fixture_test_characteristic, fixture_hello_world_lambda
) -> None:
    test_characteristic = fixture_test_characteristic
    assert test_characteristic.slug == "TEST"
    assert test_characteristic.description == "Test characteristic"
    assert test_characteristic.sub_characteristics == {
        fixture_hello_world_lambda.slug: fixture_hello_world_lambda
    }
    result_list: List[CheckType] = []
    for result in test_characteristic.check():
        result_list.append(result)
    slug, description, value, status = result_list[1]
    assert slug == "|-- " + fixture_hello_world_lambda.slug
    assert description == fixture_hello_world_lambda.description
    assert value == "Hello world."
    assert status


@pytest.fixture
def fixture_test_characteristic(fixture_hello_world_lambda):
    class TestCharacteristic(Characteristic):
        def __init__(self, slug, description):
            super().__init__(slug, description)
            self.add_sub_characteristic(fixture_hello_world_lambda)

    return TestCharacteristic("TEST", "Test characteristic")


@pytest.fixture
def fixture_hello_world_lambda() -> LambdaCharacteristic:
    """Fixture with hello world function."""
    return LambdaCharacteristic(
        "HWORLD",
        "This is an example LambdaCharacteristic.",
        "Hello world.",
        lambda x: (
            "HWORLD",
            "This is an example LambdaCharacteristic.",
            "Hello world.",
            True,
        ),
        lambda x: None,
    )
