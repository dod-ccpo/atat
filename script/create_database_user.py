#!/usr/bin/env python
# Add root application dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sqlalchemy

from atat.app import make_config, make_app
from atat.database import db


def create_database_user(username, password, dbname):
    print(
        f"Creating Postgres user role for \"{username}\" and granting all privileges to database '{dbname}'."
    )
    conn = db.engine.connect()

    meta = sqlalchemy.MetaData(bind=conn)
    meta.reflect()

    trans = conn.begin()
    engine = trans.connection.engine

    try:
        engine.execute(
            f"CREATE ROLE \"{username}\" WITH LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD '{password}'; "
            f'GRANT CREATE, CONNECT, TEMPORARY ON DATABASE "{dbname}" TO "{username}";\n'
        )
    except sqlalchemy.exc.ProgrammingError as err:
        print(f'Database role "{username}" not created')
        print(err.orig)

    trans.commit()


if __name__ == "__main__":
    config = make_config({"default": {"DEBUG": False}})
    app = make_app(config)
    with app.app_context():
        dbname = config.get("PGDATABASE", "atat")
        username = sys.argv[1]
        password = sys.argv[2]
        create_database_user(username, password, dbname)
