from enum import Enum

from sqlalchemy import Column, Integer, String, Enum as SQLAEnum

from atst.models import Base

class Source(Enum):
    MANUAL = "Manual"
    EDA = "eda"


class FundingType(Enum):
    RDTE = "RDTE"
    OM = "OM"
    PROC = "PROC"
    OTHER = "OTHER"


class TaskOrder(Base):
    __tablename__ = "task_order"

    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True)
    source = Column(SQLAEnum(Source))
    funding_type = Column(SQLAEnum(FundingType))
    funding_type_other = Column(String)
    clin_0001 = Column(Integer)
    clin_0003 = Column(Integer)
    clin_1001 = Column(Integer)
    clin_1003 = Column(Integer)
    clin_2001 = Column(Integer)
    clin_2003 = Column(Integer)
