from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form
import pendulum


class DateForm(Form):
    month = IntegerField("Month", validators=[Required()])
    day = IntegerField("Day", validators=[Required()])
    year = IntegerField("Year", validators=[Required()])

    @property
    def data(self):
        try:
            return pendulum.date(
                self.year.data, self.month.data, self.day.data
            ).isoformat()
        except TypeError:
            return None

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        if obj:
            date = pendulum.parse(obj).date()
            data = dict(year=date.year, month=date.month, day=date.day)
        super().process(formdata=formdata, obj=obj, data=data, **kwargs)
