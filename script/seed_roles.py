#! .venv/bin/python
# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from sqlalchemy.orm.exc import NoResultFound
from atat.app import make_config, make_app
from atat.database import db
from atat.models import PermissionSet
from atat.domain.permission_sets import (
    ATAT_PERMISSION_SETS,
    PORTFOLIO_PERMISSION_SETS,
    APPLICATION_PERMISSION_SETS,
)


def seed_roles():
    for permission_set_info in (
        ATAT_PERMISSION_SETS + PORTFOLIO_PERMISSION_SETS + APPLICATION_PERMISSION_SETS
    ):
        permission_set = PermissionSet(**permission_set_info)
        try:
            existing_permission_set = (
                db.session.query(PermissionSet)
                .filter_by(name=permission_set.name)
                .one()
            )
            existing_permission_set.description = permission_set.description
            existing_permission_set.permissions = permission_set.permissions
            existing_permission_set.display_name = permission_set.display_name
            db.session.add(existing_permission_set)
            print(
                "Updated existing permission_set {}".format(
                    existing_permission_set.name
                )
            )
        except NoResultFound:
            db.session.add(permission_set)
            print("Added new permission_set {}".format(permission_set.name))

    db.session.commit()


if __name__ == "__main__":
    config = make_config({"default": {"DEBUG": False,}})
    app = make_app(config)
    with app.app_context():
        seed_roles()
