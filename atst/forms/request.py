from wtforms.fields.html5 import IntegerField
from wtforms.fields import (
    RadioField,
    StringField,
    SelectField,
    FormField,
    TextAreaField,
    BooleanField
    )
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form
from .date import DateForm


class RequestForm(Form):

    # Details of Use: Overall Request Details
    dollar_value = IntegerField(
        'What is the total estimated dollar value of the cloud resources you are requesting using the JEDI CSP Calculator? ',
        validators=[Required()],
        )

    num_applications = IntegerField(
        'Please estimate the number of applications that might be supported by this request',
        validators=[Required()],
        )

    date_start = StringField(
        'Date you expect to start accessing this cloud resource',
        validators=[Required()]
        )

    app_description = TextAreaField(
        'Please briefly describe how your team is expecting to use the JEDI Cloud'
        )

    supported_organizations = StringField(
        'What organizations are supported by these applications?',
        validators=[Required()],
        )

    uii_ids = TextAreaField(
        'Please enter the Unique Item Identifier (UII)s related to your application(s) if you already have them.'
        )

    pe_id = TextAreaField(
        'Please provide the Program Element (PE) Numbers related to your request'
        )


    # Details of Use: Cloud Resources
    total_cores = IntegerField(
        'Total Number of vCPU cores',
        validators=[Required()]
        )
    total_ram = IntegerField(
        'Total RAM',
        validators=[Required()]
        )
    total_object_storage = IntegerField(
        'Total object storage',
        validators=[Required()]
        )
    total_database_storage = IntegerField(
        'Total database storage',
        validators=[Required()]
        )
    total_server_storage = IntegerField(
        'Total server storage',
        validators=[Required()]
        )


    # Details of Use: Support Staff
    has_contractor_advisor = BooleanField('Do you have a contractor to advise and assist you with using cloud services?', 
        validators=[Required()]
        )

    is_migrating_application = BooleanField('Are you using the JEDI Cloud to migrate existing applications?', 
        validators=[Required()]
        )

    supporting_organization = IntegerField(
        'Please describe the organizations that are supporting you, include both government and contractor resources',
        validators=[Required()],
        )

    has_migration_office = BooleanField(
        'Do you have a migration office that you\'re working with to migrate to the cloud?', validators=[Required()]
        )

    supporting_organization = StringField(
        'Please describe the organizations that are supporting you, include both government and contractor resources.',
        validators=[Required()]
        )


    # Organizational Info
    name = StringField(
        'Name',
        )

    email = StringField(
        'Email (associated with your CAC)',
        validators=[Required()]
        )

    phone_number = StringField(
        'Phone Number',
        validators=[Required()]
        )

    service_branch = StringField(
        'Service Branch or Agency',
        validators=[Required()]
        )

    citizenship = StringField(
        'Citizenship',
        validators=[Required()]
        )

    designation = StringField(
        'Designation of Person',
        validators=[Required()]
        )

    date_latest_training = StringField(
        'Latest Information Assurance (IA) Training completion date',
        validators=[Required()]
        )


    # Primary Government/Military POC
    name_poc = StringField(
        'Name',
        )

    email_poc = StringField(
        'Email (associated with your CAC)',
        validators=[Required()]
        )

    dodid_poc = StringField(
        'DOD ID',
        validators=[Required()]
        )

    # Financial Verification

    task_order_id = StringField(
        'Task Order Number associated with this request.',
        validators=[Required()]
        )

    name_co = StringField(
        'Contracting Officer Name',
        validators=[Required()]
        )

    email_co = StringField(
        'Contracting Officer Email',
        validators=[Required()]
        )

    office_co = StringField(
        'Contracting Office Office',
        validators=[Required()]
        )

    name_cor = StringField(
        'Contracting Officer Representative (COR) Name',
        validators=[Required()]
        )

    email_cor = StringField(
        'Contracting Officer Representative (COR) Email',
        validators=[Required()]
        )

    office_cor = StringField(
        'Contracting Officer Representative (COR) Office',
        validators=[Required()]
        )

    funding_type = StringField(
        'Funding Type',
        validators=[Required()]
        )

    funding_type_other = StringField(
        'If other, please specify',
        validators=[Required()]
        )

    clin_0001 = StringField(
        'CLIN 0001 - Unclassified IaaS and PaaS Amount',
        validators=[Required()]
        )

    clin_0003 = StringField(
        'CLIN 0003 - Unclassified Cloud Support Package',
        validators=[Required()]
        )

    clin_1001 = StringField(
        'CLIN 1001 - Unclassified IaaS and PaaS Amount OPTION PERIOD 1',
        validators=[Required()]
        )

    clin_1003 = StringField(
        'CLIN 1003 - Unclassified Cloud Support Package OPTION PERIOD 1',
        validators=[Required()]
        )

    clin_2001 = StringField(
        'CLIN 2001 - Unclassified IaaS and PaaS Amount OPTION PERIOD 2',
        validators=[Required()]
        )

    clin_2003 = StringField(
        'CLIN 2003 - Unclassified Cloud Support Package OPTION PERIOD 2',
        validators=[Required()]
        )

