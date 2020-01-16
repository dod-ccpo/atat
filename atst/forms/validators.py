from datetime import datetime
import re

from werkzeug.datastructures import FileStorage
from wtforms.validators import ValidationError
import pendulum

from atst.utils.localization import translate


REGEX_ALPHA_NUMERIC = "^[A-Za-z0-9\-_ \.]*$"


def DateRange(lower_bound=None, upper_bound=None, message=None):
    def _date_range(form, field):
        if field.data is None:
            return

        now = pendulum.now().date()

        if isinstance(field.data, str):
            date = datetime.strptime(field.data, field.format)
        else:
            date = field.data

        if lower_bound is not None:
            if (now - lower_bound) > date:
                raise ValidationError(message)

        if upper_bound is not None:
            if (now + upper_bound) < date:
                raise ValidationError(message)

    return _date_range


def IsNumber(message=translate("forms.validators.is_number_message")):
    def _is_number(form, field):
        try:
            int(field.data)
        except (ValueError, TypeError):
            raise ValidationError(message)

    return _is_number


def PhoneNumber(message=translate("forms.validators.phone_number_message")):
    def _is_phone_number(form, field):
        digits = re.sub(r"\D", "", field.data)
        if len(digits) not in [5, 10]:
            raise ValidationError(message)

        match = re.match(r"[\d\-\(\) ]+", field.data)
        if not match or match.group() != field.data:
            raise ValidationError(message)

    return _is_phone_number


def Name(message=translate("forms.validators.name_message")):
    def _name(form, field):
        match = re.match(r"[\w \,\.\'\-]+", field.data)
        if not match or match.group() != field.data:
            raise ValidationError(message)

    return _name


def ListItemRequired(
    message=translate("forms.validators.list_item_required_message"),
    empty_values=[None],
):
    def _list_item_required(form, field):
        non_empty_values = [
            v for v in field.data if (v not in empty_values and re.search(r"\S", v))
        ]
        if len(non_empty_values) == 0:
            raise ValidationError(message)

    return _list_item_required


def ListItemsUnique(message=translate("forms.validators.list_items_unique_message")):
    def _list_items_unique(form, field):
        if len(field.data) > len(set(field.data)):
            raise ValidationError(message)

    return _list_items_unique


def FileLength(max_length=50000000, message=None):
    def _file_length(_form, field):
        if field.data is None or not isinstance(field.data, FileStorage):
            return True

        content = field.data.read()
        if len(content) > max_length:
            raise ValidationError(message)
        else:
            field.data.seek(0)

    return _file_length
