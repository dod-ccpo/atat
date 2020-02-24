# Add root application dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sqlalchemy

from atat.app import make_config


def _root_connection(config, root_db):
    # Assemble DATABASE_URI value
    database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
        config.get("PGUSER"),
        config.get("PGPASSWORD"),
        config.get("PGHOST"),
        config.get("PGPORT"),
        root_db,
    )
    engine = sqlalchemy.create_engine(database_uri)
    return engine.connect()


def create_database(conn, dbname):
    conn.execute("commit")
    conn.execute(f"CREATE DATABASE {dbname};")
    conn.close()

    return True


if __name__ == "__main__":
    dbname = sys.argv[1]
    config = make_config()

    conn = _root_connection(config, "postgres")

    print(f"Creating database {dbname}")
    create_database(conn, dbname)
