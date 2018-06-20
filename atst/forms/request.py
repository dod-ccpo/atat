from wtforms.fields.html5 import IntegerField
from wtforms.fields import (
    RadioField,
    StringField,
    SelectField,
    FormField,
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
    input_estimate = SelectField(
        'How did you arrive at this estimate?',
        validators=[Required()],
        choices=[
            ('', '- Select -'),
            ('calculator', 'CSP usage calculator'),
            ('B', 'Option B'),
            ('C', 'Option C'),
        ],
    )
    # no way to apply a label to a whole nested form like this
    date_start = FormField(DateForm)
    period_of_performance = SelectField(
        'Desired period of performance',
        validators=[Required()],
        choices=[
            ('', '- Select -'),
            ('value1', '30 days'),
            ('value2', '60 days'),
            ('value3', '90 days'),
        ],
    )
    classification_level = RadioField(
        'Classification level',
        validators=[Required()],
        choices=[
            ('unclassified', 'Unclassified'),
            ('secret', 'Secret'),
            ('top-secret', 'Top Secret'),
        ],
    )
    primary_service_branch = StringField(
        'Primary service branch usage', validators=[Required()]
    )
    cloud_model = RadioField(
        'Cloud model service',
        validators=[Required()],
        choices=[('iaas', 'IaaS'), ('paas', 'PaaS'), ('both', 'Both')],
    )
    number_of_cores = IntegerField('Number of cores', validators=[Required()])
    total_ram = IntegerField('Total RAM', validators=[Required()])
    object_storage = IntegerField('Total object storage', validators=[Required()])
    server_storage = IntegerField('Total server storage', validators=[Required()])
    total_active_users = IntegerField('Total active users', validators=[Required()])
    total_peak_users = IntegerField('Total peak users', validators=[Required()])
    total_requests = IntegerField('Total requests', validators=[Required()])
    total_environments = IntegerField('Total environments', validators=[Required()])

    # this is just an example validation; obviously this is wrong.
    def validate_total_ram(self, field):
        if (field.data % 2) != 0:
            raise ValidationError("RAM must be in increments of 2.")
