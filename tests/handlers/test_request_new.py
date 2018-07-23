import re
import pytest
import tornado
import urllib
from tests.mocks import MOCK_USER
from tests.factories import RequestFactory

ERROR_CLASS = "usa-input-error-message"
MOCK_REQUEST = RequestFactory.create(
    creator=MOCK_USER["id"],
    body={
        "financial_verification": {
            "pe_id": "0203752A",
        },
    }
)

@pytest.mark.gen_test
def test_submit_invalid_request_form(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.get_current_user", lambda s: MOCK_USER
    )
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.check_xsrf_cookie", lambda s: True
    )
    # this just needs to send a known invalid form value
    response = yield http_client.fetch(
        base_url + "/requests/new",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="total_ram=5",
    )
    assert response.effective_url == base_url + "/requests/new"
    assert re.search(ERROR_CLASS, response.body.decode())


@pytest.mark.gen_test
def test_submit_valid_request_form(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.get_current_user", lambda s: MOCK_USER
    )
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.check_xsrf_cookie", lambda s: True
    )
    monkeypatch.setattr("atst.forms.request.RequestForm.validate", lambda s: True)

    # this just needs to send a known invalid form value
    response = yield http_client.fetch(
        base_url + "/requests/new",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="meaning=42",
    )
    assert "/requests/new/2" in response.effective_url
