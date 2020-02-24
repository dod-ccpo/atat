import pytest
from atat.utils.localization import all_keys, translate, LocalizationInvalidKeyError


def test_looking_up_existing_key():
    assert translate("testing.example_string") == "Hello World"


def test_nested_keys():
    assert translate("testing.nested.example") == "Hello nested example"


def test_with_variables():
    assert (
        translate("testing.example_with_variables", {"name": "Alice"})
        == "Hello, Alice!"
    )

    assert translate("testing.example_with_variables", {"name": "Bob"}) == "Hello, Bob!"


def test_looking_up_non_existent_key():
    with pytest.raises(LocalizationInvalidKeyError):
        translate("testing.an.invalid_key")


def test_all_keys():
    assert "testing.example_with_variables" in all_keys()
    assert "testing.nested.example" in all_keys()
    assert not "testing.nested.missing" in all_keys()
