import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atat.app import make_config, make_app

from atat.domain.exceptions import NotFoundError
from atat.domain.users import Users


def grant_ccpo_perms(dod_id):
    try:
        user = Users.get_by_dod_id(dod_id)
        if user.permission_sets:
            print("%s (DoD ID: %s) already CCPO user." % (user.full_name, user.dod_id))
        else:
            Users.give_ccpo_perms(user)
            print(
                "CCPO permissions successfully granted to %s (DoD ID: %s)."
                % (user.full_name, user.dod_id)
            )

    except NotFoundError:
        print("User not found.")


if __name__ == "__main__":
    config = make_config({"DISABLE_CRL_CHECK": True, "DEBUG": False})
    app = make_app(config)

    with app.app_context():
        dod_id = sys.argv[1]
        grant_ccpo_perms(dod_id)
