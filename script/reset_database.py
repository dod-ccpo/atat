#!/usr/bin/env python
# Add root application dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sqlalchemy
from alembic import config as alembic_config

from seed_roles import seed_roles
from atat.database import db
from atat.app import make_config, make_app


def reset_database():
    conn = db.engine.connect()

    meta = sqlalchemy.MetaData(bind=conn)
    meta.reflect()

    trans = conn.begin()

    # drop all tables
    meta.drop_all()
    trans.commit()

    # rerun the migrations
    alembic_config.main(argv=["upgrade", "head"])

    # seed the permission sets
    seed_roles()


if __name__ == "__main__":
    config = make_config({"default": {"DISABLE_CRL_CHECK": True, "DEBUG": False}})
    app = make_app(config)
    print(f"Creating extension {app}")
    with app.app_context():
        reset_database()
