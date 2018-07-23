import factory
from uuid import uuid4

from atst.models import Request, RequestStatusEvent


class RequestFactory(factory.Factory):
    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())
