import tornado

from atst.handler import BaseHandler
from atst.domain.requests import Requests


class RequestsSubmit(BaseHandler):
    def initialize(self, db_session):
        self.requests_repo = Requests(db_session)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, request_id):
        request = self.requests_repo.get(request_id)
        request = yield self.requests_repo.submit(request)
        if request.status == "approved":
            self.redirect("/requests?modal=True")
        else:
            self.redirect("/requests")
