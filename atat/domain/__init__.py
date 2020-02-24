from sqlalchemy.orm.exc import NoResultFound

from atat.database import db
from atat.domain.exceptions import NotFoundError


class BaseDomainClass(object):
    model = None
    resource_name = None

    @classmethod
    def get(cls, resource_id, **kwargs):
        base_query = db.session.query(cls.model).filter(cls.model.id == resource_id)
        if getattr(cls.model, "deleted", False):
            base_query = base_query.filter(cls.model.deleted == False)

        for col, val in kwargs.items():
            base_query = base_query.filter(getattr(cls.model, col) == val)

        try:
            resource = base_query.one()

            return resource
        except NoResultFound:
            raise NotFoundError(cls.resource_name)
