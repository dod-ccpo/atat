from atst.handler import BaseHandler


class Dev(BaseHandler):
    def initialize(self, action):
        self.action = action

    def get(self):
        if self.action == "login":
            self._login()

    def _login(self):
        self._start_session()
        self.redirect("/home")
