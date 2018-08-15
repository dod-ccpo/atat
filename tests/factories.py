import random
import string
import factory
from uuid import uuid4

from atst.models.request import Request
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.models.pe_number import PENumber
from atst.models.task_order import TaskOrder
from atst.models.user import User
from atst.models.role import Role
from atst.models.request_status_event import RequestStatusEvent
from atst.domain.roles import Roles



class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role

    permissions = []


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: uuid4())
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    atat_role = factory.SubFactory(RoleFactory)
    dod_id = factory.LazyFunction(lambda: "".join(random.choices(string.digits, k=10)))


class RequestStatusEventFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = RequestStatusEvent

    id = factory.Sequence(lambda x: uuid4())


class RequestFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())
    status_events = factory.RelatedFactory(
        RequestStatusEventFactory, "request", new_status=RequestStatus.STARTED
    )
    creator = factory.SubFactory(UserFactory)
    body = factory.LazyAttribute(lambda r: RequestFactory.build_request_body(r.creator))

    @classmethod
    def build_request_body(cls, user, dollar_value=1000000):
        return {
            "primary_poc": {
                "dodid_poc": user.dod_id,
                "email_poc": user.email,
                "fname_poc": user.first_name,
                "lname_poc": user.last_name
            },
            "details_of_use": {
                "jedi_usage": "adf",
                "start_date": "2018-08-08",
                "cloud_native": "yes",
                "dollar_value": dollar_value,
                "dod_component": "Army and Air Force Exchange Service",
                "data_transfers": "less_than_100gb",
                "jedi_migration": "yes",
                "num_software_systems": 1,
                "number_user_sessions": 2,
                "average_daily_traffic": 1,
                "engineering_assessment": "yes",
                "technical_support_team": "yes",
                "estimated_monthly_spend": 100,
                "average_daily_traffic_gb": 4,
                "expected_completion_date": "less_than_1_month",
                "rationalization_software_systems": "yes",
                "organization_providing_assistance": "in_house_staff"
            },
            "information_about_you": {
                "citizenship": "United States",
                "designation": "military",
                "phone_number": "1234567890",
                "email_request": user.email,
                "fname_request": user.first_name,
                "lname_request": user.last_name,
                "service_branch": "Air Force, Department of the",
                "date_latest_training": "2018-08-06"
            }
        }


class PENumberFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PENumber


class TaskOrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskOrder
