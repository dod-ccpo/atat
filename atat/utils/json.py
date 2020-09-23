import json
from datetime import date
from enum import Enum

from flask.json import JSONEncoder
from werkzeug.datastructures import FileStorage

from atat.models.attachment import Attachment


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Attachment):
            return obj.filename
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, FileStorage):
            return obj.filename
        return JSONEncoder.default(self, obj)


def sqlalchemy_dumps(dct):
    def _default(obj):
        if isinstance(obj, Enum):
            return obj.name
        else:
            raise TypeError()

    return json.dumps(dct, default=_default)
