from celery.result import AsyncResult
from sqlalchemy import Column, Integer, String

import atat.models.mixins as mixins
from atat.models.base import Base


class JobFailure(Base, mixins.TimestampsMixin):
    __tablename__ = "job_failures"

    id = Column(Integer(), primary_key=True)
    task_id = Column(String(), nullable=False)
    entity = Column(String(), nullable=False)
    entity_id = Column(String(), nullable=False)

    @property
    def task(self):
        if not hasattr(self, "_task"):
            self._task = AsyncResult(self.task_id)

        return self._task
