from wtforms.fields.html5 import IntegerField, EmailField, TelField
from wtforms.fields import BooleanField
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form
from .date import DateForm


class ReviewForm(Form):
    reviewed = BooleanField("I have reviewed this data and it is correct.")
