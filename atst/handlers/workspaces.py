from atst.handler import BaseHandler
import tornado

mock_workspaces = [
    {
        "name": "Unclassified IaaS and PaaS for Defense Digital Service (DDS)",
        "id": "5966187a-eff9-44c3-aa15-4de7a65ac7ff",
        "task_order": {"number": 123456},
        "user_count": 23,
    }
]


class Workspaces(BaseHandler):
    def initialize(self, page, db_session):
        self.page = page
        self.db_session = db_session

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        self.render("workspaces.html.to", page=self.page, workspaces=mock_workspaces)
