from enum import Enum
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from atst.models.base import Base
import atst.models.types as types
import atst.models.mixins as mixins
from atst.models.attachment import Attachment
from pendulum import today


class Status(Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    UPCOMING = "Upcoming"
    EXPIRED = "Expired"
    UNSIGNED = "Unsigned"


SORT_ORDERING = [
    Status.ACTIVE,
    Status.DRAFT,
    Status.UPCOMING,
    Status.EXPIRED,
    Status.UNSIGNED,
]


class TaskOrder(Base, mixins.TimestampsMixin):
    __tablename__ = "task_orders"

    id = types.Id()

    portfolio_id = Column(ForeignKey("portfolios.id"), nullable=False)
    portfolio = relationship("Portfolio")

    pdf_attachment_id = Column(ForeignKey("attachments.id"))
    _pdf = relationship("Attachment", foreign_keys=[pdf_attachment_id])
    pdf_last_sent_at = Column(DateTime)
    number = Column(String, unique=True,)  # Task Order Number
    signer_dod_id = Column(String)
    signed_at = Column(DateTime)

    clins = relationship(
        "CLIN", back_populates="task_order", cascade="all, delete-orphan"
    )

    @property
    def sorted_clins(self):
        return sorted(self.clins, key=lambda clin: (clin.number[1:], clin.number[0]))

    @hybrid_property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, new_pdf):
        self._pdf = self._set_attachment(new_pdf, "_pdf")

    def _set_attachment(self, new_attachment, attribute):
        if isinstance(new_attachment, Attachment):
            return new_attachment
        elif isinstance(new_attachment, dict):
            if new_attachment["filename"] and new_attachment["object_name"]:
                attachment = Attachment.get_or_create(
                    new_attachment["object_name"], new_attachment
                )
                return attachment
            else:
                return None
        elif not new_attachment and hasattr(self, attribute):
            return None
        else:
            raise TypeError("Could not set attachment with invalid type")

    @property
    def is_draft(self):
        return self.status == Status.DRAFT

    @property
    def is_active(self):
        return self.status == Status.ACTIVE

    @property
    def is_expired(self):
        return self.status == Status.EXPIRED

    @property
    def clins_are_completed(self):
        return all([len(self.clins), (clin.is_completed for clin in self.clins)])

    @property
    def is_completed(self):
        return all([self.pdf, self.number, self.clins_are_completed])

    @property
    def is_signed(self):
        return self.signed_at is not None

    @property
    def status(self):
        todays_date = today(tz="UTC").date()

        if not self.is_completed and not self.is_signed:
            return Status.DRAFT
        elif self.is_completed and not self.is_signed:
            return Status.UNSIGNED
        elif todays_date < self.start_date:
            return Status.UPCOMING
        elif todays_date > self.end_date:
            return Status.EXPIRED
        elif self.start_date <= todays_date <= self.end_date:
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
            return (self.end_date - today(tz="UTC").date()).days

    @property
    def total_obligated_funds(self):
        return sum(
            (clin.obligated_amount for clin in self.clins if clin.obligated_amount)
        )

    @property
    def total_contract_amount(self):
        return sum((clin.total_amount for clin in self.clins if clin.total_amount))

    @property
    def invoiced_funds(self):
        # TODO: implement this using reporting data from the CSP
        if self.is_active:
            return self.total_obligated_funds * Decimal(0.75)
        else:
            return 0

    @property
    def display_status(self):
        return self.status.value

    @property
    def portfolio_name(self):
        return self.portfolio.name

    def to_dictionary(self):
        return {
            "portfolio_name": self.portfolio_name,
            "pdf": self.pdf,
            "clins": [clin.to_dictionary() for clin in self.clins],
            **{
                c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name not in ["id"]
            },
        }

    def __repr__(self):
        return "<TaskOrder(number='{}', id='{}')>".format(self.number, self.id)
