from sqlalchemy import exists, and_, exc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.attributes import flag_modified

from atst.database import db
from atst.models import Request
from atst.domain.exceptions import NotFoundError


class RequestQuery(object):

    @classmethod
    def create(cls, request: Request):
        db.session.add(request)
        db.session.commit()
        return request

    @classmethod
    def exists(cls, request_id, creator) -> bool:
        try:
            return db.session.query(
                exists().where(
                    and_(Request.id == request_id, Request.creator == creator)
                )
            ).scalar()
        except exc.DataError:
            return False

    @classmethod
    def get(cls, request_id):
        try:
            request = db.session.query(Request).filter_by(id=request_id).one()
        except NoResultFound:
            raise NotFoundError("request")

        return request

    @classmethod
    def get_with_lock(cls, request_id) -> Request:
        try:
            # Query for request matching id, acquiring a row-level write lock.
            # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-FOR-UPDATE-SHARE
            request = (
                db.session.query(Request)
                .filter_by(id=request_id)
                .with_for_update(of=Request)
                .one()
            )
            return request
        except NoResultFound:
            return

    @classmethod
    def get_many(cls, creator=None):
        filters = []
        if creator:
            filters.append(Request.creator == creator)

        requests = (
            db.session.query(Request)
            .filter(*filters)
            .order_by(Request.time_created.desc())
            .all()
        )
        return requests

    @classmethod
    def update(cls, request, update_body=False) -> Request:
        # Without this, sqlalchemy won't notice the change to request.body,
        # since it doesn't track dictionary mutations by default.
        if update_body:
            flag_modified(request, "body")

        db.session.add(request)
        db.session.commit()
        return request
