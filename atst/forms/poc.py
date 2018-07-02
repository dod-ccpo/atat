from wtforms.fields.html5 import IntegerField, EmailField, TelField
from wtforms.fields import (
    RadioField,
    StringField,
    SelectField,
    FormField,
    TextAreaField,
    BooleanField,
)
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form
from .date import DateForm


class POCForm(Form):
    # Primary Government/Military POC
    fname_poc = StringField("POC First Name")
    lname_poc = StringField("POC Last Name")

    email_poc = StringField("POC Email (associated with CAC)", validators=[Required()])

    dodid_poc = StringField("DOD ID", validators=[Required()])
