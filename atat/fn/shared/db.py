import sqlalchemy
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def _get_session():
    database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
        os.environ.get("PGUSER"),
        os.environ.get("PGPASSWORD"),
        os.environ.get("PGHOST"),
        os.environ.get("PGPORT"),
        os.environ.get("PGDATABASE"),
    )

    engine = sqlalchemy.create_engine(database_uri, pool_pre_ping=True, connect_args={"sslmode": "verify-full", "sslrootcert": "DigiCertGlobalRootG2.crt.pem"})
    # engine = sqlalchemy.create_engine(database_uri, pool_pre_ping=True)
    Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    return session