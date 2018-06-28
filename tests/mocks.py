import tornado.gen
from tornado.httpclient import HTTPRequest, HTTPResponse

from atst.api_client import ApiClient


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


class MockRequestsClient(MockApiClient):
    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        json = {
            "id": "66b8ef71-86d3-48ef-abc2-51bfa1732b6b",
            "creator": "49903ae7-da4a-49bf-a6dc-9dff5d004238",
            "body": {},
        }
        return self._get_response("GET", path, 200, json=json)

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        json = {
            "id": "66b8ef71-86d3-48ef-abc2-51bfa1732b6b",
            "creator": "49903ae7-da4a-49bf-a6dc-9dff5d004238",
            "body": {},
        }
        return self._get_response("POST", path, 202, json=json)
