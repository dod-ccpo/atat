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


class RequestForm(Form):

    # Details of Use: Overall Request Details
    dollar_value = IntegerField(
        "What is the total estimated dollar value of the cloud resources you are requesting using the JEDI CSP Calculator? ",
        validators=[Required()],
    )

    num_applications = IntegerField(
        "Please estimate the number of applications that might be supported by this request",
        validators=[Required()],
    )

    date_start = StringField(
        "Date you expect to start accessing this cloud resource",
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
    total_cores = IntegerField("Total Number of vCPU cores", validators=[Required()])
    total_ram = IntegerField("Total RAM", validators=[Required()])
    total_object_storage = IntegerField("Total object storage", validators=[Required()])
    total_database_storage = IntegerField(
        "Total database storage", validators=[Required()]
    )
    total_server_storage = IntegerField("Total server storage", validators=[Required()])

    # Details of Use: Support Staff
    has_contractor_advisor = RadioField(
        "Do you have a contractor to advise and assist you with using cloud services?",
        choices=[('yes','Yes'),('no','No')],
        validators=[Required()],
    )

    is_migrating_application = RadioField(
        "Are you using the JEDI Cloud to migrate existing applications?",
        choices=[('yes','Yes'),('no','No')],
        validators=[Required()],
    )

    supporting_organization = IntegerField(
        "Please describe the organizations that are supporting you, include both government and contractor resources",
        validators=[Required()],
    )

    has_migration_office = RadioField(
        "Do you have a migration office that you're working with to migrate to the cloud?",
        choices=[('yes','Yes'),('no','No')],
        validators=[Required()],
    )

    supporting_organization = StringField(
        "Please describe the organizations that are supporting you, include both government and contractor resources.",
        validators=[Required()],
    )

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

    # Primary Government/Military POC
    fname_poc = StringField("POC First Name")
    lname_poc = StringField("POC Last Name")

    email_poc = StringField("POC Email (associated with CAC)", validators=[Required()])

    dodid_poc = StringField("DOD ID", validators=[Required()])

    # Financial Verification

    task_order_id = StringField(
        "Task Order Number associated with this request.", validators=[Required()]
    )

    fname_co = StringField("Contracting Officer First Name", validators=[Required()])
    lname_co = StringField("Contracting Officer Last Name", validators=[Required()])

    email_co = StringField("Contracting Officer Email", validators=[Required()])

    office_co = StringField("Contracting Office Office", validators=[Required()])

    fname_cor = StringField(
        "Contracting Officer Representative (COR) First Name", validators=[Required()]
    )

    lname_cor = StringField(
        "Contracting Officer Representative (COR) Last Name", validators=[Required()]
    )

    email_cor = StringField(
        "Contracting Officer Representative (COR) Email", validators=[Required()]
    )

    office_cor = StringField(
        "Contracting Officer Representative (COR) Office", validators=[Required()]
    )


    funding_type = SelectField(
        validators=[Required()],
        choices=[
            ("", "- Select -"),
            ("RDTE","Research, Development, Testing & Evaluation (RDT&E)"),
            ("OM","Operations & Maintenance (O&M)"),
            ("PROC","Procurement (PROC)"),
            ("OTHER","Other"),
        ],
    )


    funding_type_other = StringField(
        "If other, please specify", validators=[Required()]
    )

    clin_0001 = StringField(
        "CLIN 0001 - Unclassified IaaS and PaaS Amount", validators=[Required()]
    )

    clin_0003 = StringField(
        "CLIN 0003 - Unclassified Cloud Support Package", validators=[Required()]
    )

    clin_1001 = StringField(
        "CLIN 1001 - Unclassified IaaS and PaaS Amount OPTION PERIOD 1",
        validators=[Required()],
    )

    clin_1003 = StringField(
        "CLIN 1003 - Unclassified Cloud Support Package OPTION PERIOD 1",
        validators=[Required()],
    )

    clin_2001 = StringField(
        "CLIN 2001 - Unclassified IaaS and PaaS Amount OPTION PERIOD 2",
        validators=[Required()],
    )

    clin_2003 = StringField(
        "CLIN 2003 - Unclassified Cloud Support Package OPTION PERIOD 2",
        validators=[Required()],
    )