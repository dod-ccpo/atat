import re
import pytest
import tornado.web
import tornado.gen


@pytest.mark.gen_test
def test_redirects_when_not_logged_in(http_client, base_url):
    response = yield http_client.fetch(
        base_url + "/home", raise_error=False, follow_redirects=False
    )
    location = response.headers["Location"]
    assert response.code == 302
    assert response.error
    assert re.match("/\??", location)


@pytest.mark.gen_test
def test_login_with_valid_bearer_token(app, monkeypatch, http_client, base_url):
    @tornado.gen.coroutine
    def _validate_login_token(c, t):
        return True

    monkeypatch.setattr(
        "atst.handlers.login.Login._validate_login_token", _validate_login_token
    )
    response = yield http_client.fetch(
        base_url + "/login?bearer-token=abc-123",
        follow_redirects=False,
        raise_error=False,
    )
    assert response.headers["Set-Cookie"].startswith("atst")
    assert response.headers["Location"] == "/home"
    assert response.code == 302


@pytest.mark.gen_test
def test_login_via_dev_endpoint(app, http_client, base_url):
    response = yield http_client.fetch(
        base_url + "/login-dev", raise_error=False, follow_redirects=False
    )
    assert response.headers["Set-Cookie"].startswith("atst")
    assert response.code == 302
    assert response.headers["Location"] == "/home"


@pytest.mark.gen_test
@pytest.mark.skip(reason="need to work out auth error user paths")
def test_login_with_invalid_bearer_token(http_client, base_url):
    _response = yield http_client.fetch(
        base_url + "/home",
        raise_error=False,
        headers={"Cookie": "bearer-token=anything"},
    )
