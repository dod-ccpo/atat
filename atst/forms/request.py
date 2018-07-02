from wtforms.fields.html5 import IntegerField
from wtforms.fields import RadioField, StringField, TextAreaField
from wtforms.validators import Required, NumberRange
from wtforms_tornado import Form
from .fields import DateField


class RequestForm(Form):

    # Details of Use: Overall Request Details
    dollar_value = IntegerField(
        "What is the total estimated dollar value of the cloud resources you are requesting using the JEDI CSP Calculator? ",
        validators=[Required(), NumberRange(min=1)],
    )

    num_applications = IntegerField(
        "Please estimate the number of applications that might be supported by this request",
        validators=[Required(), NumberRange(min=1)],
    )

    date_start = DateField(
        "Date you expect to start accessing this cloud resource.",
        validators=[Required()],
    )

    app_description = TextAreaField(
        "Please briefly describe how your team is expecting to use the JEDI Cloud"
    )

    supported_organizations = StringField(
        "What organizations are supported by these applications?",
        validators=[Required()],
    )

    uii_ids = TextAreaField(
        "Please enter the Unique Item Identifier (UII)s related to your application(s) if you already have them."
    )

    pe_id = StringField(
        "Please provide the Program Element (PE) Numbers related to your request"
    )

    # Details of Use: Cloud Resources
    total_cores = IntegerField(
        "Total Number of vCPU cores", validators=[Required(), NumberRange(min=0)]
    )
    total_ram = IntegerField("Total RAM", validators=[Required(), NumberRange(min=0)])
    total_object_storage = IntegerField(
        "Total object storage", validators=[Required(), NumberRange(min=0)]
    )
    total_database_storage = IntegerField(
        "Total database storage", validators=[Required(), NumberRange(min=0)]
    )
    total_server_storage = IntegerField(
        "Total server storage", validators=[Required(), NumberRange(min=0)]
    )

    # Details of Use: Support Staff
    has_contractor_advisor = RadioField(
        "Do you have a contractor to advise and assist you with using cloud services?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[Required()],
    )

    is_migrating_application = RadioField(
        "Are you using the JEDI Cloud to migrate existing applications?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[Required()],
    )

    supporting_organization = TextAreaField(
        "Please describe the organizations that are supporting you, include both government and contractor resources",
        validators=[Required()],
    )

    has_migration_office = RadioField(
        "Do you have a migration office that you're working with to migrate to the cloud?",
        choices=[("yes", "Yes"), ("no", "No")],
        validators=[Required()],
    )

    supporting_organization = StringField(
        "Please describe the organizations that are supporting you, include both government and contractor resources.",
        validators=[Required()],
    )
