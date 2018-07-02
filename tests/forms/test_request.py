import wtforms
import pytest
from atst.forms.request import RequestForm

form = RequestForm()


def test_form_has_expected_fields():
    label = form.dollar_value.label
    assert "estimated dollar value" in label.text
