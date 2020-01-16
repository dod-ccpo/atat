import pendulum
from copy import deepcopy
from wtforms.fields.html5 import DateField, EmailField, TelField
from wtforms.fields import RadioField, StringField
from wtforms.validators import Email, DataRequired, Optional

from .fields import SelectField
from .forms import BaseForm
from .data import SERVICE_BRANCHES
from atst.models.user import User
from atst.utils.localization import translate
from wtforms.validators import Length
from atst.forms.validators import IsNumber

from .validators import Name, DateRange, PhoneNumber


USER_FIELDS = {
    "first_name": StringField(
        translate("forms.edit_user.first_name_label"),
        validators=[Name(), Length(max=100)],
    ),
    "last_name": StringField(
        translate("forms.edit_user.last_name_label"),
        validators=[Name(), Length(max=100)],
    ),
    "email": EmailField(translate("forms.edit_user.email_label"), validators=[Email()]),
    "phone_number": TelField(
        translate("forms.edit_user.phone_number_label"), validators=[PhoneNumber()]
    ),
    "phone_ext": StringField("Extension", validators=[IsNumber(), Length(max=10)]),
    "service_branch": SelectField(
        translate("forms.edit_user.service_branch_label"), choices=SERVICE_BRANCHES
    ),
    "citizenship": RadioField(
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ]
    ),
    "designation": RadioField(
        translate("forms.edit_user.designation_label"),
        choices=[
            ("military", "Military"),
            ("civilian", "Civilian"),
            ("contractor", "Contractor"),
        ],
    ),
    "date_latest_training": DateField(
        translate("forms.edit_user.date_latest_training_label"),
        description=translate("forms.edit_user.date_latest_training_description"),
        validators=[
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            )
        ],
        format="%m/%d/%Y",
    ),
}


def inherit_field(unbound_field, required=True):
    kwargs = deepcopy(unbound_field.kwargs)
    if not "validators" in kwargs:
        kwargs["validators"] = []

    if required:
        kwargs["validators"].append(DataRequired())
    else:
        kwargs["validators"].append(Optional())

    return unbound_field.field_class(*unbound_field.args, **kwargs)


def inherit_user_field(field_name):
    required = field_name in User.REQUIRED_FIELDS
    return inherit_field(USER_FIELDS[field_name], required=required)


class EditUserForm(BaseForm):

    first_name = inherit_user_field("first_name")
    last_name = inherit_user_field("last_name")
    email = inherit_user_field("email")
    phone_number = inherit_user_field("phone_number")
    phone_ext = inherit_user_field("phone_ext")
    service_branch = inherit_user_field("service_branch")
    citizenship = inherit_user_field("citizenship")
    designation = inherit_user_field("designation")
    date_latest_training = inherit_user_field("date_latest_training")
