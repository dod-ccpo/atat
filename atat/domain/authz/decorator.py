from functools import wraps

from flask import g, current_app as app, request

from . import user_can_access
from atat.domain.exceptions import UnauthorizedError


def check_access(permission, message, override, *args, **kwargs):
    access_args = {
        "message": message,
        "portfolio": g.portfolio,
        "application": g.application,
    }

    if override is not None and override(g.current_user, **access_args, **kwargs):
        return True

    user_can_access(g.current_user, permission, **access_args)

    return True


def user_can_access_decorator(permission, message=None, override=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                check_access(permission, message, override, *args, **kwargs)
                app.logger.info(
                    "User {} accessed {} {}".format(
                        g.current_user.id, request.method, request.path
                    ),
                    extra={"tags": ["access", "success"]},
                )

                return f(*args, **kwargs)
            except UnauthorizedError as err:
                app.logger.warning(
                    "User {} denied access {} {}".format(
                        g.current_user.id, request.method, request.path
                    ),
                    extra={"tags": ["access", "failure"]},
                )

                raise (err)

        return decorated_function

    return decorator
