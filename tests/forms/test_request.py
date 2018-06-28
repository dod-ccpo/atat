import wtforms
import pytest
from atst.forms.request import RequestForm

form = RequestForm()


def test_form_has_expected_fields():
    label = form.application_name.label
    assert label.text == "Application name"


def test_form_can_validate_total_ram():
    form.application_name.data = 5
    with pytest.raises(wtforms.validators.ValidationError):
        form.validate_total_ram(form.application_name)
