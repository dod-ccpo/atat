from wtforms.validators import ValidationError
import pendulum


def DateRange(lower_bound=None, upper_bound=None, message=None):
    def _date_range(form, field):
        now = pendulum.now().date()

        if lower_bound is not None:
            date = pendulum.parse(field.data).date()
            if (now - lower_bound) > date:
                raise ValidationError(message)

        if upper_bound is not None:
            date = pendulum.parse(field.data).date()
            if (now + upper_bound) < date:
                raise ValidationError(message)

    return _date_range


def IsNumber(message="Please enter a valid number."):
    def _is_number(form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError(message)

    return _is_number
