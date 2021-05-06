#!/usr/bin/env python
# Add root application dir to the python path
import os
import sys
import argparse

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sqlalchemy

from atat.utils.config import make_config

default_extension = "uuid-ossp"


def _create_connection(config, db):
    # Assemble DATABASE_URI value
    database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
        config.get("PGUSER"),
        config.get("PGPASSWORD"),
        config.get("PGHOST"),
        config.get("PGPORT"),
        db,
    )
    engine = sqlalchemy.create_engine(database_uri, pool_pre_ping=True)
    return engine.connect()


def create_database(conn, dbname):
    conn.execute("commit")
    conn.execute(f"CREATE DATABASE {dbname};")
    conn.close()

    return True


def create_extension(conn, extension_name):
    # Extension must be created by admin user
    conn.execute("commit")
    conn.execute(f'CREATE EXTENSION IF NOT EXISTS "{extension_name}";')
    conn.close()

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbname", help="Name of DB to create")
    parser.add_argument(
        "extension",
        nargs="?",
        default=default_extension,
        help=f"Extension to create in DB. Defaults to {default_extension} if no option provided",
    )
    args = parser.parse_args()
    dbname = args.dbname
    extension = args.extension
    config = make_config()

    root_conn = _create_connection(config, "postgres")

    print(f"Creating database {dbname}")
    create_database(root_conn, dbname)
    print(f"Creating extension {extension} on {dbname}")
    new_conn = _create_connection(config, dbname)
    create_extension(new_conn, extension)
