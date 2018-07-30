from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from atst.models import User

from .roles import Roles
from .exceptions import NotFoundError, AlreadyExistsError


class Users(object):

    def __init__(self, db_session):
        self.db_session = db_session


    def get(self, user_id):
        try:
            user = User.query.filter_by(id=user_id).one()
        except NoResultFound:
            raise NotFoundError("user")

        return user

    def create(self, user_id, atat_role_name):
        atat_role = Roles.get(atat_role_name)

        try:
            user = User(id=user_id, atat_role=atat_role)
            self.db_session.add(user)
            self.db_session.commit()
        except IntegrityError:
            raise AlreadyExistsError("user")

        return user

    def get_or_create(self, user_id, *args, **kwargs):
        created = False

        try:
            user = Users.get(user_id)
        except NotFoundError:
            user = Users.create(user_id, *args, **kwargs)
            self.db_session.add(user)
            self.db_session.commit()
            created = True

        return user, created

    def update(self, user_id, atat_role_name):

        user = Users.get(user_id)
        atat_role = Roles.get(atat_role_name)
        user.atat_role = atat_role

        self.db_session.add(user)
        self.db_session.commit()

        return user
