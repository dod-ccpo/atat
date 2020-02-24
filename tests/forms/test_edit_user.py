import pytest
from werkzeug.datastructures import ImmutableMultiDict

from atat.forms.edit_user import EditUserForm

from tests.factories import UserFactory


def test_edit_user_form_requires_all_fields():
    user = UserFactory.create()
    user_data = user.to_dictionary()
    del user_data["date_latest_training"]
    form_data = ImmutableMultiDict(user_data)
    form = EditUserForm(form_data)
    assert not form.validate()
    assert form.errors == {"date_latest_training": ["This field is required."]}


def test_edit_user_form_valid_with_all_fields():
    user = UserFactory.create()
    user_data = user.to_dictionary()
    user_data["date_latest_training"] = user_data["date_latest_training"].strftime(
        "%m/%d/%Y"
    )
    form_data = ImmutableMultiDict(user_data)
    form = EditUserForm(form_data)
    assert form.validate()
