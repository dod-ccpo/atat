from wtforms.fields.html5 import IntegerField
from wtforms.fields import RadioField, StringField, TextAreaField
from wtforms.validators import NumberRange, InputRequired
from wtforms_tornado import Form
from .fields import DateField, NewlineListField
from .validators import DateRange
import pendulum


class RequestForm(Form):

    # Details of Use: Overall Request Details
    dollar_value = IntegerField(
        "What is the total estimated dollar value of the cloud resources you are requesting using the JEDI CSP Calculator? ",
        validators=[InputRequired(), NumberRange(min=1)],
    )

    num_applications = IntegerField(
        "Please estimate the number of applications that might be supported by this request",
        validators=[InputRequired(), NumberRange(min=1)],
    )

    date_start = DateField(
        "Date you expect to start accessing this cloud resource.",
        validators=[
            InputRequired(),
            DateRange(
                lower_bound=pendulum.duration(days=0),
                message="Must be no earlier than today.",
            ),
        ],
    )

    app_description = TextAreaField(
        "Please briefly describe how your team is expecting to use the JEDI Cloud"
    )

    supported_organizations = StringField(
        "What organizations are supported by these applications?",
        validators=[InputRequired()],
    )

    # Details of Use: Cloud Resources
    total_cores = IntegerField(
        "Total Number of vCPU cores", validators=[InputRequired(), NumberRange(min=0)]
    )
    total_ram = IntegerField(
        "Total RAM", validators=[InputRequired(), NumberRange(min=0)]
    )
    total_object_storage = IntegerField(
        "Total object storage", validators=[InputRequired(), NumberRange(min=0)]
    )
    total_database_storage = IntegerField(
        "Total database storage", validators=[InputRequired(), NumberRange(min=0)]
    )
    total_server_storage = IntegerField(
        "Total server storage", validators=[InputRequired(), NumberRange(min=0)]
    )

    # Details of Use: Support Staff
    has_contractor_advisor = RadioField(
        "Do you have a contractor to advise and assist you with using cloud services?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[InputRequired()],
    )

    is_migrating_application = RadioField(
        "Are you using the JEDI Cloud to migrate existing applications?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[InputRequired()],
    )

    supporting_organization = TextAreaField(
        "Please describe the organizations that are supporting you, include both government and contractor resources",
        validators=[InputRequired()],
    )

    has_migration_office = RadioField(
        "Do you have a migration office that you're working with to migrate to the cloud?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[InputRequired()],
    )

    supporting_organization = StringField(
        "Please describe the organizations that are supporting you, include both government and contractor resources.",
        validators=[InputRequired()],
    )
