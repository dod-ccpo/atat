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
            f"CREATE ROLE \"{username}\" WITH LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD \"{password}\"; "
            f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO \"{username}\";\n"
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO \"{username}\"; \n"
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO \"{username}\"; \n"
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO \"{username}\"; \n"
        )
    except sqlalchemy.exc.ProgrammingError as err:
        print(f"Database role \"{username}\" not created")
        print(err.orig)

    try:
        # TODO: make this more configurable
        engine.execute(f"GRANT \"{username}\" TO azure_pg_admin;")
    except sqlalchemy.exc.ProgrammingError as err:
        print(f"Unable to grant new role \"{username}\" to azure_pg_admin")
        print(err.orig)

    for table in meta.tables:
        engine.execute(f"ALTER TABLE {table} OWNER TO \"{username}\";\n")

    sequence_results = engine.execute(
        "SELECT c.relname FROM pg_class c WHERE c.relkind = 'S';"
    ).fetchall()
    sequences = [p[0] for p in sequence_results]
    for sequence in sequences:
        engine.execute(f"ALTER SEQUENCE {sequence} OWNER TO \"{username}\";\n")

    trans.commit()


if __name__ == "__main__":
    config = make_config({"default": {"DISABLE_CRL_CHECK": True, "DEBUG": False}})
    app = make_app(config)
    with app.app_context():
        dbname = config.get("PGDATABASE", "atat")
        username = sys.argv[1]
        password = sys.argv[2]
        create_database_user(username, password, dbname)
