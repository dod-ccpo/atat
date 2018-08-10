from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import RadioField, StringField
from wtforms.validators import Required, Email
import pendulum
from .fields import DateField
from .forms import ValidatedForm
from .validators import DateRange, PhoneNumber, Alphabet


class OrgForm(ValidatedForm):
    fname_request = StringField("First Name", validators=[Required(), Alphabet()])

    lname_request = StringField("Last Name", validators=[Required(), Alphabet()])

    email_request = EmailField("Email Address", validators=[Required(), Email()])

    phone_number = TelField("Phone Number", validators=[Required(), PhoneNumber()])

    service_branch = StringField(
        "Service Branch or Agency",
        description="Which services and organizations do you belong to within the DoD?",
        validators=[Required()]
    )

    citizenship = RadioField(
        description="What is your citizenship status?",
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ],
        validators=[Required()],
    )

    designation = RadioField(
        "Designation of Person",
        description="What is your designation within the DoD?",
        choices=[
            ("military", "Military"),
            ("civilian", "Civilian"),
            ("contractor", "Contractor"),
        ],
        validators=[Required()],
    )

    date_latest_training = DateField(
        "Latest Information Assurance (IA) Training completion date",
        description="To complete the training, you can find it in <a class=\"icon-link\" href=\"https://iatraining.disa.mil/eta/disa_cac2018/launchPage.htm\" target=\"_blank\">Information Assurance Cyber Awareness Challange</a> website.",
        validators=[
            Required(),
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            ),
        ],
    )
