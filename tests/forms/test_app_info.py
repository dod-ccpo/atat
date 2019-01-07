import pytest

from atst.forms.task_order import AppInfoForm
from tests.factories import TaskOrderFactory


def test_validations_pass_for_valid_form():
    form_data = TaskOrderFactory.dictionary()
    form_data["portfolio_name"] = "Dummy"

    form = AppInfoForm(form_data)

    assert form.validate()


def test_validations_fail_for_invalid_form():
    form = AppInfoForm({})

    assert not form.validate()

    errors = form.errors

    def assert_field_is_required(field, errors):
        assert "This field is required." in errors[field]

    def assert_none_is_not_valid_choice(field, errors):
        assert "Not a valid choice" in errors[field]

    assert_field_is_required("complexity", errors)
    assert_field_is_required("dev_team", errors)
    assert_field_is_required("portfolio_name", errors)
    assert_field_is_required("scope", errors)

    assert_none_is_not_valid_choice("app_migration", errors)
    assert_none_is_not_valid_choice("defense_component", errors)
    assert_none_is_not_valid_choice("native_apps", errors)
    assert_none_is_not_valid_choice("team_experience", errors)


def test_validations_skipped_for_draft():
    form = AppInfoForm({"is_draft": True})

    assert form.validate()
