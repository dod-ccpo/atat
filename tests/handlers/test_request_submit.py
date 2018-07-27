import pytest
import tornado
from tests.mocks import MOCK_USER
from tests.factories import RequestFactory


@tornado.gen.coroutine
def _mock_func(*args, **kwargs):
    return RequestFactory.create()


@pytest.mark.gen_test
def test_submit_reviewed_request(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.get_current_user",
        lambda s: MOCK_USER,
    )
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.check_xsrf_cookie", lambda s: True
    )
    monkeypatch.setattr("atst.domain.requests.Requests.get", _mock_func)
    monkeypatch.setattr("atst.domain.requests.Requests.submit", _mock_func)
    monkeypatch.setattr("atst.models.request.Request.status", "pending")
    # this just needs to send a known invalid form value
    response = yield http_client.fetch(
        base_url + "/requests/submit/1",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="",
        raise_error=False,
        follow_redirects=False,
    )
    assert response.headers["Location"] == "/requests"


@pytest.mark.gen_test
def test_submit_autoapproved_reviewed_request(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.get_current_user",
        lambda s: MOCK_USER,
    )
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.check_xsrf_cookie", lambda s: True
    )
    monkeypatch.setattr("atst.domain.requests.Requests.get", _mock_func)
    monkeypatch.setattr("atst.domain.requests.Requests.submit", _mock_func)
    monkeypatch.setattr("atst.models.request.Request.status", "approved")
    # this just needs to send a known invalid form value
    response = yield http_client.fetch(
        base_url + "/requests/submit/1",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="",
        raise_error=False,
        follow_redirects=False,
    )
    assert response.headers["Location"] == "/requests?modal=True"
