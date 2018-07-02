from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import RadioField, StringField
from wtforms.validators import Required, Length, Email
from wtforms_tornado import Form
from .fields import DateField


class OrgForm(Form):
    fname_request = StringField("First Name", validators=[Required()])
    lname_request = StringField("Last Name", validators=[Required()])

    email_request = EmailField(
        "Email (associated with your CAC)", validators=[Required(), Email()]
    )

    phone_number = TelField("Phone Number", validators=[Required(), Length(min=7)])

    service_branch = StringField("Service Branch or Agency", validators=[Required()])

    citizenship = RadioField(
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ],
        validators=[Required()],
    )

    designation = StringField("Designation of Person", validators=[Required()])

    date_latest_training = DateField(
        "Latest Information Assurance (IA) Training completion date.",
        validators=[Required()],
    )
