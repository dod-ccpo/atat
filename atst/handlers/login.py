import tornado
from atst.handler import BaseHandler


class Login(BaseHandler):
    def initialize(self, authnid_client):
        self.authnid_client = authnid_client

    @tornado.gen.coroutine
    def get(self):
        token = self.get_query_argument("bearer-token")
        if token:
            valid = yield self._validate_login_token(token)
            if valid:
                self._start_session()
                self.redirect("/home")
                return

        url = self.get_login_url()
        self.redirect(url)
        return

    @tornado.gen.coroutine
    def _validate_login_token(self, token):
        try:
            response = yield self.authnid_client.post(
                "/validate", json={"token": token}
            )
            return response.code == 200

        except tornado.httpclient.HTTPError as error:
            if error.response.code == 401:
                return False

            else:
                raise error
