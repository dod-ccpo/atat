import pytest
from werkzeug.datastructures import ImmutableMultiDict

from atat.forms.edit_user import EditUserForm
from tests.factories import UserFactory


def test_edit_user_form_requires_all_fields():
    user = UserFactory.create()
    user_data = user.to_dictionary()
    del user_data["email"]
    form_data = ImmutableMultiDict(user_data)
    form = EditUserForm(form_data)
    assert not form.validate()
    assert form.errors == {"email": ["This field is required."]}


def test_edit_user_form_valid_with_all_fields():
    user = UserFactory.create()
    user_data = user.to_dictionary()
    user_data["email"] = "updated@email.com"
    form_data = ImmutableMultiDict(user_data)
    form = EditUserForm(form_data)
    assert form.validate()
