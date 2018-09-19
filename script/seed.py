# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atst.database import db
from atst.app import make_config, make_app
from atst.domain.users import Users
from atst.domain.requests import Requests
from atst.domain.workspaces import Workspaces
from atst.domain.projects import Projects
from atst.domain.exceptions import AlreadyExistsError
from tests.factories import RequestFactory
from atst.routes.dev import _DEV_USERS as DEV_USERS

WORKSPACE_USERS = [
    {
        "first_name": "Danny",
        "last_name": "Knight",
        "email": "knight@mil.gov",
        "workspace_role": "developer",
        "dod_id": "0000000001"
    },
    {
        "first_name": "Mario",
        "last_name": "Hudson",
        "email": "hudson@mil.gov",
        "workspace_role": "ccpo",
        "dod_id": "0000000002"
    },
    {
        "first_name": "Louise",
        "last_name": "Greer",
        "email": "greer@mil.gov",
        "workspace_role": "admin",
        "dod_id": "0000000003"
    },
]

def seed_db():
    users = []
    for dev_user in DEV_USERS.values():
        try:
            user = Users.create(**dev_user)
        except AlreadyExistsError:
            user = Users.get_by_dod_id(dev_user["dod_id"])

        users.append(user)

    for user in users:
        if Requests.get_many(creator=user):
            continue

        requests = []
        for dollar_value in [1, 200, 3000, 40000, 500000, 1000000]:
            request = RequestFactory.build(creator=user)
            request.latest_revision.dollar_value = dollar_value
            db.session.add(request)
            db.session.commit()

            Requests.submit(user, request)
            requests.append(request)

        workspace = Workspaces.create(requests[0], name="{}'s workspace".format(user.first_name))
        for workspace_user in WORKSPACE_USERS:
            Workspaces.create_member(user, workspace, workspace_user)

        Projects.create(
            user,
            workspace=workspace,
            name="First Project",
            description="This is our first project.",
            environment_names=["dev", "staging", "prod"]
        )


if __name__ == "__main__":
    config = make_config()
    app = make_app(config)
    with app.app_context():
        seed_db()
