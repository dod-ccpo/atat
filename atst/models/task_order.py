from enum import Enum
from datetime import date, datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from werkzeug.datastructures import FileStorage

from atst.models import Attachment, Base, mixins, types
from atst.models.clin import JEDICLINType


class Status(Enum):
    STARTED = "Started"
    PENDING = "Pending"
    ACTIVE = "Active"
    EXPIRED = "Expired"
    DRAFT = "Draft"
    UPCOMING = "Upcoming"
    UNSIGNED = "Unsigned"


class TaskOrder(Base, mixins.TimestampsMixin):
    __tablename__ = "task_orders"

    id = types.Id()

    portfolio_id = Column(ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio")

    user_id = Column(ForeignKey("users.id"))
    creator = relationship("User", foreign_keys="TaskOrder.user_id")

    pdf_attachment_id = Column(ForeignKey("attachments.id"))
    _pdf = relationship("Attachment", foreign_keys=[pdf_attachment_id])
    number = Column(String, unique=True)  # Task Order Number
    signer_dod_id = Column(String)
    signed_at = Column(DateTime)

    clins = relationship("CLIN")

    @hybrid_property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, new_pdf):
        self._pdf = self._set_attachment(new_pdf, "_pdf")

    def _set_attachment(self, new_attachment, attribute):
        if isinstance(new_attachment, Attachment):
            return new_attachment
        elif isinstance(new_attachment, FileStorage):
            return Attachment.attach(new_attachment, "task_order", self.id)
        elif not new_attachment and hasattr(self, attribute):
            return None
        else:
            raise TypeError("Could not set attachment with invalid type")

    @property
    def is_active(self):
        return self.status == Status.ACTIVE

    @property
    def is_expired(self):
        return self.status == Status.EXPIRED

    @property
    def is_completed(self):
        return all([self.pdf, self.number, len(self.clins)])

    @property
    def is_signed(self):
        return self.signed_at is not None

    @property
    def status(self):
        today = date.today()

        if not self.is_completed and not self.is_signed:
            return Status.DRAFT
        elif self.is_completed and not self.is_signed:
            return Status.UNSIGNED
        elif today < self.start_date:
            return Status.UPCOMING
        elif today >= self.end_date:
            return Status.EXPIRED
        elif self.start_date <= today < self.end_date:
            return Status.ACTIVE

    @property
    def start_date(self):
        return min((c.start_date for c in self.clins), default=None)

    @property
    def end_date(self):
        return max((c.end_date for c in self.clins), default=None)

    @property
    def days_to_expiration(self):
        if self.end_date:
            return (self.end_date - date.today()).days

    @property
    def total_obligated_funds(self):
        total = 0
        for clin in self.clins:
            if clin.jedi_clin_type in [
                JEDICLINType.JEDI_CLIN_1,
                JEDICLINType.JEDI_CLIN_3,
            ]:
                total += clin.obligated_amount
        return total

    @property
    def total_contract_amount(self):
        total = 0
        for clin in self.clins:
            total += clin.obligated_amount
        return total

    @property
    # TODO delete when we delete task_order_review flow
    def budget(self):
        return 100000

    @property
    def balance(self):
        # TODO: fix task order -- reimplement using CLINs
        # Faked for display purposes
        return 50

    @property
    def display_status(self):
        return self.status.value

    @property
    def portfolio_name(self):
        return self.portfolio.name

    @property
    def is_pending(self):
        return self.status == Status.PENDING

    def to_dictionary(self):
        return {
            "portfolio_name": self.portfolio_name,
            **{
                c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name not in ["id"]
            },
        }

    def __repr__(self):
        return "<TaskOrder(number='{}', id='{}')>".format(self.number, self.id)
