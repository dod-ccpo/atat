import factory
from uuid import uuid4

from atst.models import Request, RequestStatusEvent
from atst.models.pe_number import PENumber
from atst.models.task_order import TaskOrder


class RequestFactory(factory.Factory):
    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())

class PENumberFactory(factory.Factory):
    class Meta:
        model = PENumber

class TaskOrderFactory(factory.Factory):
    class Meta:
        model = TaskOrder
