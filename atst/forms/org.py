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


class OrgForm(Form):
    # Organizational Info
    fname_request = StringField("First Name")
    lname_request = StringField("Last Name")

    email_request = EmailField("Email (associated with your CAC)", validators=[Required()])

    phone_number = TelField("Phone Number", validators=[Required()])

    service_branch = StringField("Service Branch or Agency", validators=[Required()])

    citizenship = RadioField(
        choices=[
            ('United States','United States'),
            ('Foreign National','Foreign National'),
            ('Other','Other')],
        validators=[Required()]
    )

    designation = StringField("Designation of Person", validators=[Required()])

    date_latest_training = FormField(DateForm)
