import tornado.gen
from tornado.httpclient import HTTPRequest, HTTPResponse

from atst.api_client import ApiClient
from tests.factories import RequestFactory


MOCK_USER = {
    "id": "9cb348f0-8102-4962-88c4-dac8180c904c",
    "email": "fake.user@mail.com",
    "first_name": "Fake",
    "last_name": "User",
}
MOCK_REQUEST = RequestFactory.create(
    creator=MOCK_USER["id"],
    body={
        "financial_verification": {
            "pe_id": "0203752A",
        },
    }
)


class MockApiClient(ApiClient):

    def __init__(self, service):
        self.service = service

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return self._get_response("GET", path)

    @tornado.gen.coroutine
    def put(self, path, **kwargs):
        return self._get_response("PUT", path)

    @tornado.gen.coroutine
    def patch(self, path, **kwargs):
        return self._get_response("PATCH", path)

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return self._get_response("POST", path)

    @tornado.gen.coroutine
    def delete(self, path, **kwargs):
        return self._get_response("DELETE", path)

    def _get_response(self, verb, path, code=200, json=None):
        response = HTTPResponse(
            request=HTTPRequest(path, verb),
            code=code,
            headers={"Content-Type": "application/json"},
        )

        setattr(response, "ok", 200 <= code < 300)
        if json:
            setattr(response, "json", json)

        return response


MOCK_VALID_PE_ID = "8675309U"
