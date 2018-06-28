import tornado
import pendulum

from atst.handler import BaseHandler


def map_request(user, request):
    time_created = pendulum.parse(request["time_created"])
    is_new = time_created.add(days=1) > pendulum.now()

    return {
        "order_id": request["id"],
        "is_new": is_new,
        "status": request["status"],
        "app_count": 1,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": "{} {}".format(user["first_name"], user["last_name"]),
    }


class Request(BaseHandler):
    def initialize(self, page, requests_client):
        self.page = page
        self.requests_client = requests_client

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()
        response = yield self.requests_client.get(
            "/users/{}/requests".format(user["id"])
        )
        requests = response.json["requests"]
        mapped_requests = [map_request(user, request) for request in requests]
        self.render("requests.html.to", page=self.page, requests=mapped_requests)
