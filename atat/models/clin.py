from enum import Enum

import pendulum
from sqlalchemy import Column, Date, DateTime
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

import atat.models.mixins as mixins
import atat.models.types as types
from atat.models.base import Base


class JEDICLINType(Enum):
    JEDI_CLIN_1 = "JEDI_CLIN_1"
    JEDI_CLIN_2 = "JEDI_CLIN_2"
    JEDI_CLIN_3 = "JEDI_CLIN_3"
    JEDI_CLIN_4 = "JEDI_CLIN_4"


class CLIN(Base, mixins.TimestampsMixin):
    __tablename__ = "clins"

    id = types.Id()

    task_order_id = Column(ForeignKey("task_orders.id"), nullable=False)
    task_order = relationship("TaskOrder")

    number = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(scale=2), nullable=False)
    obligated_amount = Column(Numeric(scale=2), nullable=False)
    jedi_clin_type = Column(SQLAEnum(JEDICLINType, native_enum=False), nullable=False)
    last_sent_at = Column(DateTime)

    #
    # NOTE: For now obligated CLINS are CLIN 1 + CLIN 3
    #
    def is_obligated(self):
        return self.jedi_clin_type in [
            JEDICLINType.JEDI_CLIN_1,
            JEDICLINType.JEDI_CLIN_3,
        ]

    @property
    def type(self):
        return "Base" if self.number[0] == "0" else "Option"

    @property
    def is_completed(self):
        return all(
            [
                self.number,
                self.start_date,
                self.end_date,
                self.total_amount,
                self.obligated_amount,
                self.jedi_clin_type,
            ]
        )

    @property
    def jedi_clin_number(self):
        return self.jedi_clin_type.value[-1]

    def to_dictionary(self):
        data = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id"]
        }

        return data

    @property
    def is_within_pop(self):
        return pendulum.today(tz="UTC").date() in pendulum.period(
            self.start_date, self.end_date
        )

    @property
    def is_active(self):
        return self.is_within_pop and self.task_order.signed_at
