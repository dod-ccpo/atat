from webassets import Environment, Bundle
import tornado.web
from atst.home import home

assets = Environment(directory=home.child("scss"), url="/static")
css = Bundle(
    "atat.scss",
    filters="scss",
    output="../static/assets/out.css",
    depends=("**/*.scss"),
)

assets.register("css", css)
helpers = {"assets": assets}


class BaseHandler(tornado.web.RequestHandler):
    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        helpers["config"] = self.application.config
        ns.update(helpers)
        return ns

    def get_current_user(self):
        if self.get_secure_cookie("atst"):
            return {
                "id": "9cb348f0-8102-4962-88c4-dac8180c904c",
                "email": "fake.user@mail.com",
                "first_name": "Fake",
                "last_name": "User",
            }
        else:
            return None

    # this is a temporary implementation until we have real sessions
    def _start_session(self):
        self.set_secure_cookie("atst", "valid-user-session")
