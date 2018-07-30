import tornado.web
from atst.assets import environment
from atst.sessions import SessionNotFoundError
from atst.domain.users import Users

helpers = {"assets": environment}


class BaseHandler(tornado.web.RequestHandler):

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        helpers["config"] = self.application.config
        ns.update(helpers)
        return ns

    @tornado.gen.coroutine
    def login(self, user):
        db_user = yield self._get_user_permissions(user["id"])
        user["atat_permissions"] = db_user.atat_permissions
        user["atat_role"] = db_user.atat_role.name
        session_id = self.sessions.start_session(user)
        self.set_secure_cookie("atat", session_id)
        return self.redirect("/home")

    @tornado.gen.coroutine
    def _get_user_permissions(self, user_id):
        user_repo = Users(self.db_session)
        user = user_repo.get_or_create(user_id, atat_role_name="developer")
        return user

    def get_current_user(self):
        cookie = self.get_secure_cookie("atat")
        if cookie:
            try:
                session = self.application.sessions.get_session(cookie)
            except SessionNotFoundError:
                self.clear_cookie("atat")
                return None

        else:
            return None

        return session["user"]
