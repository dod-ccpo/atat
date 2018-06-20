from wtforms_tornado import Form
from wtforms.fields import StringField, RadioField, FormField
from wtforms.validators import Required
from .date import DateForm


class OrganizationInfoForm(Form):
    name = StringField('Name', validators=[Required()])
    email = StringField('Email', validators=[Required()])
    phone_number = StringField('Phone Number', validators=[Required()])
    service_branch = StringField('Service Branch / Agency', validators=[Required()])
    citizenship = RadioField('Citizenship',
                             validators=[Required()],
                             choices=[
                                 ('united_states', 'United States'),
                                 ('foreign_national', 'Foreign National'),
                                 ('other', 'Other')
                             ])
    designation = RadioField('Designation of Person',
                             validators=[Required()],
                             choices=[
                                 ('military', 'Military'),
                                 ('civilian', 'Civilian'),
                                 ('contractor', 'Contractor')
                             ])
    ia_training_completion_date = FormField(
        DateForm, 'Last IA Training Completion Date')
    collab_name = StringField('Name', validators=[Required()])
    collab_email = StringField('Email', validators=[Required()])
