from wtforms.fields.html5 import IntegerField, DateField
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form
import pendulum


class DateField(DateField):
    def _value(self):
        if self.data:
            return pendulum.parse(self.data).date()
        else:
            return None

    def process_formdata(self, values):
        if values:
            self.data = values[0]
        else:
            self.data = []
