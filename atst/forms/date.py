from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form


class DateForm(Form):
    month = IntegerField("Month", validators=[Required()])
    day = IntegerField("Day", validators=[Required()])
    year = IntegerField("Year", validators=[Required()])
