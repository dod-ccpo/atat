from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm.exc import NoResultFound

from atat.models.base import Base
import atat.models.mixins as mixins
import atat.models.types as types
from atat.database import db
from atat.domain.exceptions import NotFoundError


class AttachmentError(Exception):
    pass


class Attachment(Base, mixins.TimestampsMixin):
    __tablename__ = "attachments"

    id = types.Id()
    filename = Column(String, nullable=False)
    object_name = Column(String, unique=True, nullable=False)
    resource = Column(String)
    resource_id = Column(UUID(as_uuid=True), index=True)

    @classmethod
    def get_or_create(cls, object_name, params):
        try:
            return db.session.query(Attachment).filter_by(object_name=object_name).one()
        except NoResultFound:
            new_attachment = cls(**params)
            db.session.add(new_attachment)
            db.session.commit()
            return new_attachment

    @classmethod
    def get(cls, id_):
        try:
            return db.session.query(Attachment).filter_by(id=id_).one()
        except NoResultFound:
            raise NotFoundError("attachment")

    @classmethod
    def get_for_resource(cls, resource, resource_id):
        try:
            return (
                db.session.query(Attachment)
                .filter_by(resource=resource, resource_id=resource_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("attachment")

    @classmethod
    def delete_for_resource(cls, resource, resource_id):
        try:
            return (
                db.session.query(Attachment)
                .filter_by(resource=resource, resource_id=resource_id)
                .update({"resource_id": None})
            )
        except NoResultFound:
            raise NotFoundError("attachment")

    def __repr__(self):
        return "<Attachment(name='{}', id='{}')>".format(self.filename, self.id)
