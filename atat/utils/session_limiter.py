from flask import current_app as app

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

        app.logger.info(
            "The previous session [%s %s] is deleted for user: %s.",
            self.session_prefix,
            user.last_session_id,
            user.full_name,
        )
        self._delete_session(user.last_session_id)

        app.logger.info(
            "A new Session %s%s is assigned for user: %s.",
            self.session_prefix,
            session_id,
            user.full_name,
        )
        Users.update_last_session_id(user, session_id)

    def _delete_session(self, session_id):
        self.redis.delete(f"{self.session_prefix}{session_id}")
        app.logger.info("%s %s is deleted from Redis.", self.session_prefix, session_id)
