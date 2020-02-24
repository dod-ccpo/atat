from flask_wtf import FlaskForm
from flask import current_app, request as http_request
import re

from atat.utils.flash import formatted_flash as flash

EMPTY_LIST_FIELD = ["", None]


def remove_empty_string(value):
    # only return strings that contain non whitespace characters
    if value and re.search(r"\S", value):
        return value.strip()
    else:
        return None


class BaseForm(FlaskForm):
    def __init__(self, formdata=None, **kwargs):
        # initialize the form with data from the cache
        formdata = formdata or {}
        cached_data = current_app.form_cache.from_request(http_request)
        cached_data.update(formdata)
        super().__init__(cached_data, **kwargs)

    @property
    def data(self):
        # remove 'csrf_token' key/value pair
        # remove empty strings and None from list fields
        # prevent values that are not an option in a RadioField from being saved to the DB
        _data = super().data
        _data.pop("csrf_token", None)
        for field in _data:
            if _data[field].__class__.__name__ == "list":
                _data[field] = [el for el in _data[field] if el not in EMPTY_LIST_FIELD]
            if self[field].__class__.__name__ == "RadioField":
                choices = [el[0] for el in self[field].choices]
                if _data[field] not in choices:
                    _data[field] = None
        return _data

    def validate(self, *args, flash_invalid=True, **kwargs):
        valid = super().validate(*args, **kwargs)
        if not valid and flash_invalid:
            flash("form_errors")
        return valid
