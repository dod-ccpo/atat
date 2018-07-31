from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def make_db(config):
    engine = create_engine(config['default']['DATABASE_URI'])
    session = scoped_session(sessionmaker(bind=engine))
    return session
