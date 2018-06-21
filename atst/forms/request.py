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
    dollar_value = IntegerField(
        'What is the total estimated dollar value of the cloud resources you are requesting using the JEDI CSP Calculator? ',
        validators=[Required()],
    )
    num_applications = IntegerField(
        'Please estimate the number of applications that might be supported by this request',
        validators=[Required()],
    )
    total_cores = IntegerField('Total Number of vCPU cores', validators=[Required()])
    total_ram = IntegerField('Total RAM', validators=[Required()])
    total_object_storage = IntegerField('Total object storage', validators=[Required()])
    total_server_storage = IntegerField('Total server storage', validators=[Required()])

    date_start = FormField(DateForm, 'Date you expect to start accessing this cloud resource', validators=[Required()])
    app_description = TextAreaField('Please briefly describe how your team is expecting to use the JEDI Cloud')
    service_branch = StringField(
        'Which service branches will this resource be supporting?', validators=[Required()]
    )
    has_contractor_advisor = BooleanField('Do you have a contractor to advise and assist you with using cloud services?', validators=[Required()])
    has_migration_office = BooleanField("Do you have a migration office that you're working with to migrate to the cloud?", validators=[Required()])
    working_with = TextAreaField('Please describe who you are working with')])
    is_existing_app = BooleanField('Is this an existing site/application?', validators=[Required()])

    uiis = TextAreaField('Please provide the Unique Item Identifier (UII)s related to your request')
    pes = TextAreaField('Please provide the Program Element (PE) Numbers related to your request')
