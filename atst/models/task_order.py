from sqlalchemy import Column, Integer, String

from atst.models import Base

class TaskOrder(Base):
    __tablename__ = "task_order"

    id = Column(Integer, primary_key=True)
    number = Column(String)
