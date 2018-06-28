import pytest

from atst.api_client import ApiClient


@pytest.mark.gen_test
def test_api_client(http_client, base_url):
    client = ApiClient(base_url)
    response = yield client.get("")
    assert response.code == 200
