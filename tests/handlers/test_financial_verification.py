import re
import pytest
import tornado
import urllib
from tests.mocks import MOCK_REQUEST, MOCK_USER
from tests.factories import PENumberFactory


class TestPENumberInForm:

    required_data = {
        "pe_id": "123",
        "task_order_id": "1234567899C0001",
        "fname_co": "Contracting",
        "lname_co": "Officer",
        "email_co": "jane@mail.mil",
        "office_co": "WHS",
        "fname_cor": "Officer",
        "lname_cor": "Representative",
        "email_cor": "jane@mail.mil",
        "office_cor": "WHS",
        "funding_type": "RDTE",
        "funding_type_other": "other",
        "clin_0001": "50,000",
        "clin_0003": "13,000",
        "clin_1001": "30,000",
        "clin_1003": "7,000",
        "clin_2001": "30,000",
        "clin_2003": "7,000",
    }

    def _set_monkeypatches(self, monkeypatch):
        monkeypatch.setattr(
            "atst.handlers.request_financial_verification.RequestFinancialVerification.get_current_user", lambda s: MOCK_USER
        )
        monkeypatch.setattr(
            "atst.handlers.request_financial_verification.RequestFinancialVerification.check_xsrf_cookie", lambda s: True
        )
        monkeypatch.setattr("atst.forms.request.RequestForm.validate", lambda s: True)
        monkeypatch.setattr("atst.domain.requests.Requests.get", lambda s, i: MOCK_REQUEST)

    @tornado.gen.coroutine
    def submit_data(self, http_client, base_url, data):
        response = yield http_client.fetch(
            base_url + "/requests/verify/{}".format(MOCK_REQUEST.id),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urllib.parse.urlencode(data),
            follow_redirects=False,
            raise_error=False,
        )
        return response

    @pytest.mark.gen_test
    def test_submit_request_form_with_invalid_pe_id(self, monkeypatch, http_client, base_url):
        self._set_monkeypatches(monkeypatch)

        response = yield self.submit_data(http_client, base_url, self.required_data)

        assert "We couldn\'t find that PE number" in response.body.decode()
        assert response.code == 200
        assert "/requests/verify" in response.effective_url

    @pytest.mark.gen_test
    def test_submit_request_form_with_unchanged_pe_id(self, monkeypatch, http_client, base_url):
        self._set_monkeypatches(monkeypatch)

        data = dict(self.required_data)
        data['pe_id'] = MOCK_REQUEST.body['financial_verification']['pe_id']

        response = yield self.submit_data(http_client, base_url, data)

        assert response.code == 302
        assert response.headers.get("Location") == "/requests/financial_verification_submitted"

    @pytest.mark.gen_test
    def test_submit_request_form_with_new_valid_pe_id(self, db, monkeypatch, http_client, base_url):
        self._set_monkeypatches(monkeypatch)
        pe = PENumberFactory.create(number="8675309U", description="sample PE number")
        db.add(pe)
        db.commit()

        data = dict(self.required_data)
        data['pe_id'] = pe.number

        response = yield self.submit_data(http_client, base_url, data)

        assert response.code == 302
        assert response.headers.get("Location") == "/requests/financial_verification_submitted"
