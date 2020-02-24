import pytest
from werkzeug.datastructures import ImmutableMultiDict

from atat.utils.form_cache import DEFAULT_CACHE_NAME, FormCache


@pytest.fixture
def form_cache(app):
    return FormCache(app.redis)


def test_cache_form_data(app, form_cache):
    data = ImmutableMultiDict({"kessel_run": "12 parsecs"})
    key = form_cache.write(data)
    assert app.redis.get("{}:{}".format(DEFAULT_CACHE_NAME, key))


def test_retrieve_form_data(form_cache):
    data = ImmutableMultiDict({"class": "corellian"})
    key = form_cache.write(data)
    retrieved = form_cache.read(key)
    assert retrieved == data
