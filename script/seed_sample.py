# Add root application dir to the python path
import os
import sys
from datetime import timedelta, date, timedelta
import random
from faker import Faker

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atst.app import make_config, make_app
from atst.database import db

from atst.models.application import Application
from atst.models.environment_role import CSPRole

from atst.domain.application_roles import ApplicationRoles
from atst.domain.applications import Applications
from atst.domain.csp.reports import MockReportingProvider
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import AlreadyExistsError, NotFoundError
from atst.domain.permission_sets import PermissionSets, APPLICATION_PERMISSION_SETS
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.portfolios import Portfolios
from atst.domain.users import Users

from atst.routes.dev import _DEV_USERS as DEV_USERS

from tests.factories import (
    random_service_branch,
    random_task_order_number,
    TaskOrderFactory,
    CLINFactory,
)

fake = Faker()


PORTFOLIO_USERS = [
    {
        "first_name": "Danny",
        "last_name": "Knight",
        "email": "knight@mil.gov",
        "dod_id": "0000000001",
        "permission_sets": PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS,
    },
    {
        "first_name": "Mario",
        "last_name": "Hudson",
        "email": "hudson@mil.gov",
        "dod_id": "0000000002",
        "permission_sets": PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS,
    },
    {
        "first_name": "Louise",
        "last_name": "Greer",
        "email": "greer@mil.gov",
        "dod_id": "0000000003",
        "permission_sets": PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS,
    },
]


APPLICATION_USERS = [
    {
        "first_name": "Jean Luc",
        "last_name": "Picard",
        "email": "picard@mil.gov",
        "dod_id": "0000000004",
        "permission_sets": random.sample(
            APPLICATION_PERMISSION_SETS, k=random.randint(1, 4)
        ),
    },
    {
        "first_name": "()",
        "last_name": "Spock",
        "email": "spock@mil.gov",
        "dod_id": "0000000005",
        "permission_sets": random.sample(
            APPLICATION_PERMISSION_SETS, k=random.randint(1, 4)
        ),
    },
    {
        "first_name": "William",
        "last_name": "Shatner",
        "email": "shatner@mil.gov",
        "dod_id": "0000000006",
        "permission_sets": random.sample(
            APPLICATION_PERMISSION_SETS, k=random.randint(1, 4)
        ),
    },
    {
        "first_name": "Nyota",
        "last_name": "Uhura",
        "email": "uhura@mil.gov",
        "dod_id": "0000000007",
        "permission_sets": random.sample(
            APPLICATION_PERMISSION_SETS, k=random.randint(1, 4)
        ),
    },
    {
        "first_name": "Kathryn",
        "last_name": "Janeway",
        "email": "janeway@mil.gov",
        "dod_id": "0000000008",
        "permission_sets": random.sample(
            APPLICATION_PERMISSION_SETS, k=random.randint(1, 4)
        ),
    },
]


SHIP_NAMES = [
    "Millenium Falcon",
    "Star Destroyer",
    "Attack Cruiser",
    "Sith Infiltrator",
    "Death Star",
    "Lambda Shuttle",
    "Corellian Corvette",
]


SOFTWARE_WORDS = [
    "Enterprise",
    "Scalable",
    "Solution",
    "Blockchain",
    "Cloud",
    "Micro",
    "Macro",
    "Software",
    "Global",
    "Team",
]


ENVIRONMENT_NAMES = ["production", "staging", "test", "uat", "dev", "qa"]


def get_users():
    users = []
    for dev_user in DEV_USERS.values():
        try:
            user = Users.create(**dev_user)
        except AlreadyExistsError:
            user = Users.get_by_dod_id(dev_user["dod_id"])

        users.append(user)
    return users


def add_members_to_portfolio(portfolio):
    for user_data in PORTFOLIO_USERS:
        invite = Portfolios.invite(portfolio, portfolio.owner, user_data)
        user = Users.get_or_create_by_dod_id(user_data["dod_id"])
        PortfolioRoles.enable(invite.role, user)

    db.session.commit()


def add_task_orders_to_portfolio(portfolio):
    today = date.today()
    future = today + timedelta(days=100)
    yesterday = today - timedelta(days=1)

    draft_to = TaskOrderFactory.build(portfolio=portfolio, pdf=None)
    unsigned_to = TaskOrderFactory.build(portfolio=portfolio)
    upcoming_to = TaskOrderFactory.build(portfolio=portfolio, signed_at=yesterday)
    expired_to = TaskOrderFactory.build(portfolio=portfolio, signed_at=yesterday)
    active_to = TaskOrderFactory.build(portfolio=portfolio, signed_at=yesterday)

    clins = [
        CLINFactory.build(task_order=unsigned_to, start_date=today, end_date=today),
        CLINFactory.build(task_order=upcoming_to, start_date=future, end_date=future),
        CLINFactory.build(
            task_order=expired_to, start_date=yesterday, end_date=yesterday
        ),
        CLINFactory.build(task_order=active_to, start_date=yesterday, end_date=future),
    ]

    task_orders = [draft_to, unsigned_to, upcoming_to, expired_to, active_to]

    db.session.add_all(task_orders + clins)
    db.session.commit()


def random_applications():
    return [
        {
            "name": fake.sentence(nb_words=3, ext_word_list=SOFTWARE_WORDS)[0:-1],
            "description": fake.bs(),
            "environments": random.sample(ENVIRONMENT_NAMES, k=random.randint(1, 4)),
        }
        for n in range(random.randint(1, 4))
    ]


def add_applications_to_portfolio(portfolio):
    applications = random_applications()
    for application_data in applications:
        application = Applications.create(
            portfolio=portfolio,
            name=application_data["name"],
            description=application_data["description"],
            environment_names=application_data["environments"],
        )

        users = random.sample(APPLICATION_USERS, k=random.randint(1, 5))
        for user_data in users:
            try:
                user = Users.get_by_dod_id(user_data["dod_id"])
            except NotFoundError:
                user = Users.create(
                    user_data["dod_id"],
                    None,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                )

            app_role = ApplicationRoles.create(
                user=user,
                application=application,
                permission_set_names=[PermissionSets.EDIT_APPLICATION_TEAM],
            )

            user_environments = random.sample(
                application.environments,
                k=random.randint(1, len(application.environments)),
            )
            for env in user_environments:
                role = random.choice([e.value for e in CSPRole])
                EnvironmentRoles.create(
                    application_role=app_role, environment=env, role=role
                )


def create_demo_portfolio(name, data):
    try:
        portfolio_owner = Users.get_or_create_by_dod_id("2345678901")  # Amanda
        # auditor = Users.get_by_dod_id("3453453453")  # Sally
    except NotFoundError:
        print(
            "Could not find demo users; will not create demo portfolio {}".format(name)
        )
        return

    portfolio = Portfolios.create(
        user=portfolio_owner,
        portfolio_attrs={"name": name, "defense_component": random_service_branch()},
    )

    add_task_orders_to_portfolio(portfolio)
    add_members_to_portfolio(portfolio)

    for mock_application in data["applications"]:
        application = Application(
            portfolio=portfolio, name=mock_application.name, description=""
        )
        env_names = [env.name for env in mock_application.environments]
        envs = Environments.create_many(application, env_names)
        db.session.add(application)
        db.session.commit()


def seed_db():
    get_users()
    amanda = Users.get_by_dod_id("2345678901")

    # Create Portfolios for Amanda with mocked reporting data
    create_demo_portfolio("A-Wing", MockReportingProvider.REPORT_FIXTURE_MAP["A-Wing"])
    create_demo_portfolio("B-Wing", MockReportingProvider.REPORT_FIXTURE_MAP["B-Wing"])

    tie_interceptor = Portfolios.create(
        user=amanda,
        portfolio_attrs={
            "name": "TIE Interceptor",
            "defense_component": random_service_branch(),
        },
    )
    add_task_orders_to_portfolio(tie_interceptor)
    add_members_to_portfolio(tie_interceptor)
    add_applications_to_portfolio(tie_interceptor)

    tie_fighter = Portfolios.create(
        user=amanda,
        portfolio_attrs={
            "name": "TIE Fighter",
            "defense_component": random_service_branch(),
        },
    )
    add_task_orders_to_portfolio(tie_fighter)
    add_members_to_portfolio(tie_fighter)
    add_applications_to_portfolio(tie_fighter)

    # create a portfolio for each user
    ships = SHIP_NAMES.copy()
    for user in get_users():
        ship = random.choice(ships)
        ships.remove(ship)
        portfolio = Portfolios.create(
            user=user,
            portfolio_attrs={
                "name": ship,
                "defense_component": random_service_branch(),
            },
        )
        add_task_orders_to_portfolio(portfolio)
        add_members_to_portfolio(portfolio)
        add_applications_to_portfolio(portfolio)


if __name__ == "__main__":
    config = make_config({"DISABLE_CRL_CHECK": True, "DEBUG": False})
    app = make_app(config)
    with app.app_context():
        seed_db()
