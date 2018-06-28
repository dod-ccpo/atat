import pytest


@pytest.mark.gen_test
def test_routes(http_client, base_url):
    for path in (
        "/",
        "/home",
        "/workspaces",
        "/requests",
        "/requests/new",
        "/requests/new/1",
        "/users",
        "/reports",
        "/calculator",
    ):
        response = yield http_client.fetch(base_url + path)
    assert response.code == 200
