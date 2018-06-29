import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from json import dumps, loads, decoder


class ApiClient(object):
    def __init__(self, base_url, api_version=None, validate_cert=True):
        self.base_url = base_url
        if api_version:
            self.base_url = f"{base_url}/api/{api_version}"
        self.client = AsyncHTTPClient()
        self.validate_cert = validate_cert

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return (yield self.make_request("GET", self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def put(self, path, **kwargs):
        return (yield self.make_request("PUT", self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return (yield self.make_request("POST", self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def patch(self, path, **kwargs):
        return (yield self.make_request("PATCH", self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def delete(self, path, **kwargs):
        return (yield self.make_request("DELETE", self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def make_request(self, method, url, **kwargs):
        # If 'json' kwarg is specified, serialize it to 'body' and update
        # the Content-Type.
        if "json" in kwargs:
            kwargs["body"] = dumps(kwargs["json"])
            del kwargs["json"]
            headers = kwargs.get("headers", {})
            headers["Content-Type"] = "application/json"
            kwargs["headers"] = headers
        if not "validate_cert" in kwargs:
            kwargs["validate_cert"] = self.validate_cert

        response = yield self.client.fetch(url, method=method, **kwargs)
        return self.adapt_response(response)

    def adapt_response(self, response):
        if "application/json" in response.headers["Content-Type"]:
            try:
                json = loads(response.body)
                setattr(response, "json", json)
            except decoder.JSONDecodeError:
                setattr(response, "json", {})
        else:
            setattr(response, "json", {})
        setattr(response, "ok", 200 <= response.code < 300)
        return response
