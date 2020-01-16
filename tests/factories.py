import operator
import random
import string
import factory
from uuid import uuid4
import datetime

from atst.forms import data
from atst.models import *

from atst.domain.invitations import PortfolioInvitations
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolio_roles import PortfolioRoles


def random_choice(choices):
    return random.choice([k for k, v in choices if k])


def random_service_branch():
    return random_choice(data.SERVICE_BRANCHES)


def random_defense_component():
    return [random_choice(data.SERVICE_BRANCHES)]


def random_dod_id():
    return "".join(random.choices(string.digits, k=10))


def random_phone_number():
    return "".join(random.choices(string.digits, k=10))


def random_task_order_number():
    return "".join(random.choices(string.digits, k=10))


def random_clin_number():
    return "".join(random.choices(string.digits, k=4))


def random_past_date(year_min=1, year_max=5):
    return _random_date(year_min, year_max, operator.sub)


def random_future_date(year_min=1, year_max=5):
    return _random_date(year_min, year_max, operator.add)


def _random_date(year_min, year_max, operation):
    if year_min == year_max:
        inc = year_min
    else:
        inc = random.randrange(year_min, year_max)

    return datetime.date(
        operation(datetime.date.today().year, inc),
        random.randrange(1, 12),
        random.randrange(1, 28),
    )


def base_portfolio_permission_sets():
    return [
        PermissionSets.get(prms)
        for prms in PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS
    ]


def base_application_permission_sets():
    return [PermissionSets.get(PermissionSets.VIEW_APPLICATION)]


def get_all_portfolio_permission_sets():
    return PermissionSets.get_many(PortfolioRoles.PORTFOLIO_PERMISSION_SETS)


class Base(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def dictionary(cls, **attrs):
        return factory.build(dict, FACTORY_CLASS=cls, **attrs)


class UserFactory(Base):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: uuid4())
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    permission_sets = []
    dod_id = factory.LazyFunction(random_dod_id)
    phone_number = factory.LazyFunction(random_phone_number)
    service_branch = factory.LazyFunction(random_service_branch)
    citizenship = "United States"
    designation = "military"
    date_latest_training = factory.LazyFunction(
        lambda: datetime.date.today()
        + datetime.timedelta(days=-(random.randrange(1, 365)))
    )

    @classmethod
    def create_ccpo(cls, **kwargs):
        return cls.create(permission_sets=PermissionSets.get_all(), **kwargs)


class PortfolioFactory(Base):
    class Meta:
        model = Portfolio

    name = factory.Faker("domain_word")
    defense_component = factory.LazyFunction(random_defense_component)
    description = factory.Faker("sentence")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_applications = kwargs.pop("applications", [])
        owner = kwargs.pop("owner", UserFactory.create())
        members = kwargs.pop("members", [])
        with_task_orders = kwargs.pop("task_orders", [])

        portfolio = super()._create(model_class, *args, **kwargs)

        applications = [
            ApplicationFactory.create(portfolio=portfolio, **p)
            for p in with_applications
        ]

        task_orders = [
            TaskOrderFactory.create(portfolio=portfolio, **to)
            for to in with_task_orders
        ]

        PortfolioRoleFactory.create(
            portfolio=portfolio,
            user=owner,
            status=PortfolioRoleStatus.ACTIVE,
            permission_sets=get_all_portfolio_permission_sets(),
        )

        for member in members:
            user = member.get("user", UserFactory.create())
            role_name = member["role_name"]

            perms_set = None
            if member.get("permissions_sets"):
                perms_set = [
                    PermissionSets.get(perm_set)
                    for perm_set in member.get("permission_sets")
                ]
            else:
                perms_set = []

            PortfolioRoleFactory.create(
                portfolio=portfolio,
                user=user,
                status=PortfolioRoleStatus.ACTIVE,
                permission_sets=perms_set,
            )

        portfolio.applications = applications
        portfolio.task_orders = task_orders
        return portfolio


class ApplicationFactory(Base):
    class Meta:
        model = Application

    portfolio = factory.SubFactory(PortfolioFactory)
    name = factory.Faker("domain_word")
    description = "A test application"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_environments = kwargs.pop("environments", [])
        application = super()._create(model_class, *args, **kwargs)

        environments = [
            EnvironmentFactory.create(application=application, **e)
            for e in with_environments
        ]

        application.environments = environments
        return application


class EnvironmentFactory(Base):
    class Meta:
        model = Environment

    name = factory.Faker("domain_word")
    application = factory.SubFactory(ApplicationFactory)
    creator = factory.SubFactory(UserFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_members = kwargs.pop("members", [])
        environment = super()._create(model_class, *args, **kwargs)

        for member in with_members:
            user = member.get("user", UserFactory.create())
            application_role = ApplicationRoleFactory.create(
                application=environment.application, user=user
            )
            role_name = member["role_name"]
            EnvironmentRoleFactory.create(
                environment=environment,
                role=role_name,
                application_role=application_role,
            )

        return environment


class PortfolioRoleFactory(Base):
    class Meta:
        model = PortfolioRole

    portfolio = factory.SubFactory(PortfolioFactory)
    user = factory.SubFactory(UserFactory)
    status = PortfolioRoleStatus.PENDING
    permission_sets = factory.LazyFunction(base_portfolio_permission_sets)


class ApplicationRoleFactory(Base):
    class Meta:
        model = ApplicationRole

    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    status = ApplicationRoleStatus.PENDING
    permission_sets = factory.LazyFunction(base_application_permission_sets)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_invite = kwargs.pop("invite", True)
        app_role = model_class(*args, **kwargs)

        if with_invite and app_role.user:
            ApplicationInvitationFactory.create(
                role=app_role,
                dod_id=app_role.user.dod_id,
                first_name=app_role.user.first_name,
                last_name=app_role.user.last_name,
                email=app_role.user.email,
            )
        elif with_invite:
            ApplicationInvitationFactory.create(role=app_role)

        return app_role


class EnvironmentRoleFactory(Base):
    class Meta:
        model = EnvironmentRole

    environment = factory.SubFactory(EnvironmentFactory)
    role = random.choice([e for e in CSPRole])
    application_role = factory.SubFactory(ApplicationRoleFactory)


class PortfolioInvitationFactory(Base):
    class Meta:
        model = PortfolioInvitation

    email = factory.Faker("email")
    status = InvitationStatus.PENDING
    expiration_time = PortfolioInvitations.current_expiration_time()
    dod_id = factory.LazyFunction(random_dod_id)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        inviter_id = kwargs.pop("inviter_id", UserFactory.create().id)
        return super()._create(model_class, inviter_id=inviter_id, *args, **kwargs)


class ApplicationInvitationFactory(Base):
    class Meta:
        model = ApplicationInvitation

    email = factory.Faker("email")
    status = InvitationStatus.PENDING
    expiration_time = PortfolioInvitations.current_expiration_time()
    role = factory.SubFactory(ApplicationRoleFactory, invite=False)
    dod_id = factory.LazyFunction(random_dod_id)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        inviter_id = kwargs.pop("inviter_id", UserFactory.create().id)
        return super()._create(model_class, inviter_id=inviter_id, *args, **kwargs)


class AttachmentFactory(Base):
    class Meta:
        model = Attachment

    filename = factory.Faker("file_name", extension="pdf")
    object_name = factory.LazyFunction(lambda *args: uuid4().hex)


class TaskOrderFactory(Base):
    class Meta:
        model = TaskOrder

    portfolio = factory.SubFactory(PortfolioFactory)
    number = factory.LazyFunction(random_task_order_number)
    signed_at = None
    _pdf = factory.SubFactory(AttachmentFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        create_clins = kwargs.pop("create_clins", [])
        task_order = super()._create(model_class, *args, **kwargs)

        for clin in create_clins:
            CLINFactory.create(task_order=task_order, **clin)

        return task_order


class CLINFactory(Base):
    class Meta:
        model = CLIN

    task_order = factory.SubFactory(TaskOrderFactory)
    number = factory.LazyFunction(random_clin_number)
    start_date = datetime.date.today()
    end_date = factory.LazyFunction(random_future_date)
    total_amount = factory.LazyFunction(lambda *args: random.randint(50000, 999999))
    obligated_amount = factory.LazyFunction(lambda *args: random.randint(100, 50000))
    jedi_clin_type = factory.LazyFunction(
        lambda *args: random.choice(list(clin.JEDICLINType))
    )


class NotificationRecipientFactory(Base):
    class Meta:
        model = NotificationRecipient

    email = factory.Faker("email")


class PortfolioStateMachineFactory(Base):
    class Meta:
        model = PortfolioStateMachine

    portfolio = factory.SubFactory(PortfolioFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        portfolio = kwargs.pop("portfolio", PortfolioFactory.create())
        kwargs.update({"portfolio": portfolio})
        fsm = super()._create(model_class, *args, **kwargs)
        return fsm
