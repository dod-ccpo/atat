from wtforms.fields.html5 import DateField
from wtforms.fields import Field
from wtforms.widgets import TextArea
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


class NewlineListField(Field):
    widget = TextArea()

    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [l.strip() for l in valuelist[0].split("\n")]
        else:
            self.data = []
