#!/usr/bin/env python
# Add root application dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import yaml

from atat.app import make_config, make_app
from atat.database import db
from atat.domain.users import Users
from atat.models import User


def add_ccpo_users(ccpo_users):
    print("Creating initial set of CCPO users.")
    for user_data in ccpo_users:
        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            dod_id=user_data["dod_id"],
            email=user_data.get("email"),
            phone_number=user_data.get("phone_number"),
            phone_ext=user_data.get("phone_ext"),
        )
        Users.give_ccpo_perms(user, commit=False)
        db.session.add(user)

    db.session.commit()


def _load_yaml(file_):
    with open(file_) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config = make_config({"default": {"DEBUG": False}})
    app = make_app(config)
    with app.app_context():
        ccpo_user_file = sys.argv[1]
        ccpo_users = _load_yaml(ccpo_user_file)
        add_ccpo_users(ccpo_users)
