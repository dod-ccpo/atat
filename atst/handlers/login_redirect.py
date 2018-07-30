import tornado
from atst.handler import BaseHandler


class LoginRedirect(BaseHandler):
    def initialize(self, authnid_client, sessions, db_session):
        self.db_session = db_session
        self.authnid_client = authnid_client
        self.sessions = sessions

    @tornado.gen.coroutine
    def get(self):
        token = self.get_query_argument("bearer-token")
        if token:
            user = yield self._fetch_user_info(token)
            if user:
                yield self.login(user)
            else:
                self.write_error(401)

        url = self.get_login_url()
        self.redirect(url)

    @tornado.gen.coroutine
    def _fetch_user_info(self, token):
        try:
            response = yield self.authnid_client.post(
                "/validate", json={"token": token}
            )
            if response.code == 200:
                return response.json["user"]

        except tornado.httpclient.HTTPError as error:
            if error.response.code == 401:
                return None

            else:
                raise error
