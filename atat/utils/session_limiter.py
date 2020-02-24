from atat.domain.users import Users


class SessionLimiter(object):
    def __init__(self, config, session, redis):
        self.limit_logins = config["LIMIT_CONCURRENT_SESSIONS"]
        self.session_prefix = config.get("SESSION_KEY_PREFIX", "session:")
        self.session = session
        self.redis = redis

    def on_login(self, user):
        if not self.limit_logins:
            return

        session_id = self.session.sid
        self._delete_session(user.last_session_id)
        Users.update_last_session_id(user, session_id)

    def _delete_session(self, session_id):
        self.redis.delete(f"{self.session_prefix}{session_id}")
