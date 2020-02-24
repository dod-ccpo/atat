import pytest
from wtforms.fields import RadioField, FieldList, StringField
from werkzeug.datastructures import ImmutableMultiDict

from atat.forms.forms import BaseForm, remove_empty_string


class FormWithChoices(BaseForm):
    force_side = RadioField(
        "Choose your side",
        choices=[
            ("light", "Light Side"),
            ("dark", "Dark Side"),
            ("neutral", "Chaotic Neutral"),
        ],
    )


class FormWithList(BaseForm):
    fancy_list = FieldList(
        StringField("a very fancy list", filters=[remove_empty_string])
    )


class TestBaseForm:
    class Foo:
        person = {"force_side": None}

    obj = Foo()

    def test_radio_field_saves_only_as_choice(self):
        form_data_1 = ImmutableMultiDict({"force_side": "None"})
        form_1 = FormWithChoices(form_data_1, obj=self.obj)
        assert form_1.data["force_side"] is None

        form_data_2 = ImmutableMultiDict({"force_side": "a fake choice"})
        form_2 = FormWithChoices(form_data_2, obj=self.obj)
        assert form_2.data["force_side"] is None

        form_data_3 = ImmutableMultiDict({"force_side": "dark"})
        form_3 = FormWithChoices(form_data_3, obj=self.obj)
        assert form_3.data["force_side"] is "dark"

    @pytest.mark.parametrize(
        "form_data",
        [["testing", "", "QA"], ["testing", "    ", "QA"], ["testing", None, "QA"]],
    )
    def test_blank_list_items_removed(self, form_data):
        form = FormWithList(fancy_list=form_data)
        assert form.validate(flash_invalid=False)
        assert not form.data == ["testing", "QA"]

    def test_remove_empty_string_clips_whitespace(self):
        form = FormWithList(fancy_list=[" QA", "  testing   "])
        assert form.validate(flash_invalid=False)
        assert form.fancy_list.data == ["QA", "testing"]
