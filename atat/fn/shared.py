import json
import logging
import os

import sqlalchemy
# from atat.app import make_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from atat.models import Portfolio

def get_portfolios():
    # config = make_config()
    pfs = _get_session().query(Portfolio).all()
    logging.info(f"Found {len(pfs)} Portfolio(s).")
    return json.dumps(pfs, cls=PortfolioEncoder)


def _get_session():
    database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
        os.environ.get("PGUSER"),
        os.environ.get("PGPASSWORD"),
        os.environ.get("PGHOST"),
        os.environ.get("PGPORT"),
        os.environ.get("PGDATABASE"),
    )

    engine = sqlalchemy.create_engine(database_uri, pool_pre_ping=True, connect_args={"sslmode": "verify-full", "sslrootcert": "DigiCertGlobalRootG2.crt.pem"})
    Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    return session


class PortfolioEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Portfolio):
            # return (obj.id.hex, obj.name, obj.description)
            return {
                "id": obj.id.hex,
                "name": obj.name,
                "description": obj.description
            }
        return json.JSONEncoder.default(self, obj)
