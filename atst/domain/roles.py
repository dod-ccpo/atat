from sqlalchemy.orm.exc import NoResultFound

from atst.models import Role
from .exceptions import NotFoundError


class Roles(object):
    def __init__(self, db_session):
        self.db_session = db_session

    def get(self, role_name):
        try:
            role = self.db_session.query(Role).filter_by(name=role_name).one()
        except NoResultFound:
            raise NotFoundError("role")

        return role

    def get_all(self):
        return self.db_session.query(Role).all()
