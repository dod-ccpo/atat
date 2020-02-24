from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

from atat.domain.exceptions import NotFoundError
from atat.database import db


class Paginator(object):
    """
    Uses the Flask-SQLAlchemy extension's pagination method to paginate
    a query set.

    Also acts as a proxy object so that the results of the query set can be iterated
    over without needing to call `.items`.
    """

    def __init__(self, query_set):
        self.query_set = query_set

    @classmethod
    def get_pagination_opts(cls, request, default_page=1, default_per_page=100):
        return {
            "page": int(request.args.get("page", default_page)),
            "per_page": int(request.args.get("perPage", default_per_page)),
        }

    @classmethod
    def paginate(cls, query, pagination_opts=None):
        if pagination_opts is not None:
            return cls(
                query.paginate(
                    page=pagination_opts["page"], per_page=pagination_opts["per_page"]
                )
            )
        else:
            return query.all()

    def __getattr__(self, name):
        return getattr(self.query_set, name)

    def __iter__(self):
        return self.items.__iter__()

    def __len__(self):
        return self.items.__len__()


class Query(object):

    model = None

    @property
    def resource_name(cls):
        return cls.model.__class__.lower()

    @classmethod
    def create(cls, **kwargs):
        # pylint: disable=E1102
        return cls.model(**kwargs)

    @classmethod
    def get(cls, id_):
        try:
            resource = db.session.query(cls.model).filter_by(id=id_).one()
            return resource
        except (NoResultFound, DataError):
            raise NotFoundError(cls.resource_name)

    @classmethod
    def get_all(cls):
        return db.session.query(cls.model).all()

    @classmethod
    def add_and_commit(cls, resource):
        db.session.add(resource)
        db.session.commit()
        return resource

    @classmethod
    def paginate(cls, query, pagination_opts):
        return Paginator.paginate(query, pagination_opts)
