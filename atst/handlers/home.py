from atst.handler import BaseHandler


class Home(BaseHandler):
    def initialize(self, page):
        self.page = page

    def get(self):
        self.render("%s.html.to" % self.page, page=self.page)
