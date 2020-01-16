from wtforms.fields import (
    BooleanField,
    DecimalField,
    FieldList,
    FormField,
    StringField,
    HiddenField,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Length, NumberRange, ValidationError, Regexp
from flask_wtf import FlaskForm
from numbers import Number

from .data import JEDI_CLIN_TYPES
from .fields import SelectField
from .forms import BaseForm, remove_empty_string
from atst.utils.localization import translate
from .validators import REGEX_ALPHA_NUMERIC
from flask import current_app as app

MAX_CLIN_AMOUNT = 1000000000


def coerce_enum(enum_inst):
    if getattr(enum_inst, "value", None):
        return enum_inst.value
    else:
        return enum_inst


def validate_funding(form, field):
    if (
        isinstance(form.total_amount.data, Number)
        and isinstance(field.data, Number)
        and form.total_amount.data < field.data
    ):
        raise ValidationError(
            translate("forms.task_order.clin_funding_errors.obligated_amount_error")
        )


def validate_date_in_range(form, field):
    contract_start = app.config.get("CONTRACT_START_DATE")
    contract_end = app.config.get("CONTRACT_END_DATE")

    if field.data and (field.data < contract_start or field.data > contract_end):
        raise ValidationError(
            translate(
                "forms.task_order.pop_errors.range",
                {
                    "start": contract_start.strftime("%b %d, %Y"),
                    "end": contract_end.strftime("%b %d, %Y"),
                },
            )
        )


class CLINForm(FlaskForm):
    jedi_clin_type = SelectField(
        translate("task_orders.form.clin_type_label"),
        choices=JEDI_CLIN_TYPES,
        coerce=coerce_enum,
    )

    number = StringField(label=translate("task_orders.form.clin_number_label"))
    start_date = DateField(
        translate("task_orders.form.pop_start"),
        description=translate("task_orders.form.pop_example"),
        format="%m/%d/%Y",
        validators=[validate_date_in_range],
    )
    end_date = DateField(
        translate("task_orders.form.pop_end"),
        description=translate("task_orders.form.pop_example"),
        format="%m/%d/%Y",
        validators=[validate_date_in_range],
    )
    total_amount = DecimalField(
        label=translate("task_orders.form.total_funds_label"),
        validators=[
            NumberRange(
                0,
                MAX_CLIN_AMOUNT,
                translate("forms.task_order.clin_funding_errors.funding_range_error"),
            )
        ],
    )
    obligated_amount = DecimalField(
        label=translate("task_orders.form.obligated_funds_label"),
        validators=[
            validate_funding,
            NumberRange(
                0,
                MAX_CLIN_AMOUNT,
                translate("forms.task_order.clin_funding_errors.funding_range_error"),
            ),
        ],
    )

    def validate(self, *args, **kwargs):
        valid = super().validate(*args, **kwargs)

        if (
            self.start_date.data
            and self.end_date.data
            and self.start_date.data > self.end_date.data
        ):
            self.start_date.errors.append(
                translate("forms.task_order.pop_errors.date_order")
            )
            valid = False

        return valid


class AttachmentForm(BaseForm):
    filename = HiddenField(
        id="attachment_filename",
        validators=[
            Length(
                max=100, message=translate("forms.attachment.filename.length_error")
            ),
            Regexp(regex=REGEX_ALPHA_NUMERIC),
        ],
    )
    object_name = HiddenField(
        id="attachment_object_name",
        validators=[
            Length(
                max=40, message=translate("forms.attachment.object_name.length_error")
            ),
            Regexp(regex=REGEX_ALPHA_NUMERIC),
        ],
    )
    accept = ".pdf,application/pdf"

    def validate(self, *args, **kwargs):
        return super().validate(*args, **{**kwargs, "flash_invalid": False})


class TaskOrderForm(BaseForm):
    number = StringField(
        label=translate("forms.task_order.number_description"),
        filters=[remove_empty_string],
    )
    pdf = FormField(
        AttachmentForm,
        label=translate("task_orders.form.supporting_docs_size_limit"),
        description=translate("task_orders.form.supporting_docs_size_limit"),
    )
    clins = FieldList(FormField(CLINForm))


class SignatureForm(BaseForm):
    signature = BooleanField(
        translate("task_orders.sign.digital_signature_description"),
        validators=[Required()],
    )
    confirm = BooleanField(
        translate("task_orders.sign.confirmation_description"), validators=[Required()],
    )
