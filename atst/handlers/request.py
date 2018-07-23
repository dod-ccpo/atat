import tornado
import pendulum

from atst.handler import BaseHandler
from atst.domain.requests import Requests


def map_request(user, request):
    time_created = pendulum.instance(request.time_created)
    is_new = time_created.add(days=1) > pendulum.now()

    return {
        "order_id": request.id,
        "is_new": is_new,
        "status": request.status,
        "app_count": 1,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": "{} {}".format(user["first_name"], user["last_name"]),
    }


class Request(BaseHandler):
    def initialize(self, page, db_session):
        self.page = page
        self.requests = Requests(db_session)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()
        requests = yield self.fetch_requests(user)
        mapped_requests = [map_request(user, request) for request in requests]
        self.render("requests.html.to", page=self.page, requests=mapped_requests)

    @tornado.gen.coroutine
    def fetch_requests(self, user):
        requests = []
        if "review_and_approve_jedi_workspace_request" in user["atat_permissions"]:
            requests = self.requests.get_many()
        else:
            requests = self.requests.get_many(creator_id=user["id"])

        return requests
