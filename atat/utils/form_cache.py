from hashlib import sha256
import json
from werkzeug.datastructures import MultiDict


DEFAULT_CACHE_NAME = "formcache"


class FormCache(object):
    PARAM_NAME = "formCache"

    def __init__(self, redis):
        self.redis = redis

    def from_request(self, http_request):
        cache_key = http_request.args.get(self.PARAM_NAME)
        if cache_key:
            return self.read(cache_key)
        return MultiDict()

    def write(self, formdata, expiry_seconds=3600, key_prefix=DEFAULT_CACHE_NAME):
        value = json.dumps(formdata)
        hash_ = self._hash()
        self.redis.setex(
            name=self._key(key_prefix, hash_), value=value, time=expiry_seconds
        )
        return hash_

    def read(self, formdata_key, key_prefix=DEFAULT_CACHE_NAME):
        data = self.redis.get(self._key(key_prefix, formdata_key))
        dict_data = json.loads(data) if data is not None else {}
        return MultiDict(dict_data)

    @staticmethod
    def _key(prefix, hash_):
        return "{}:{}".format(prefix, hash_)

    @staticmethod
    def _hash():
        return sha256().hexdigest()
