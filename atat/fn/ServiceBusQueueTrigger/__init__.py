import logging

import azure.functions as func


def main(msg: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 msg.get_body().decode('utf-8'))
    # config = make_config()
    # pfs = _get_session(config).query(Portfolio).all()
    # print(f"Found {len(pfs)} portfolios")
    # print(f"{dict(pfs)}")

#
# def _get_session(config):
#     database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
#         config.get("PGUSER"),
#         config.get("PGPASSWORD"),
#         config.get("PGHOST"),
#         config.get("PGPORT"),
#         config.get("PGDATABASE"),
#     )
#     engine = sqlalchemy.create_engine(database_uri, pool_pre_ping=True)
#     Base = declarative_base()
#     Base.metadata.create_all(engine)
#     Session = sessionmaker(bind=engine)
#     Session.configure(bind=engine)
#     session = Session()
#     return session