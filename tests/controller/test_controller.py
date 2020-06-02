"""PyTest tests for controller class."""
import pytest

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
        fixture_hello_world_lambda,
    ]
    for slug, description, (value, status) in fixture_test_controller.run_check(
        fixture_hello_world_lambda.slug
    ):
        assert slug == fixture_hello_world_lambda.slug
        assert description == fixture_hello_world_lambda.description
        assert value, status == fixture_hello_world_lambda.check()


def test_run_checks(
    fixture_test_controller, fixture_test_characteristic, fixture_hello_world_lambda
) -> None:
    """Test if controller runs all checks"""
    controller = fixture_test_controller
    for slug, description, (value, status) in controller.run_checks():
        pass
        # print(f"{slug} - {description} -- {value} - {status}")


@pytest.fixture
def fixture_test_controller(
    fixture_hello_world_lambda, fixture_test_characteristic, monkeypatch
):
    controller: Controller = Controller()
    monkeypatch.setattr(
        controller,
        "characteristics",
        {
            fixture_test_characteristic.slug: fixture_test_characteristic,
            fixture_hello_world_lambda.slug: fixture_hello_world_lambda,
        },
    )
    return controller
