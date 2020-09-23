import uuid

from atat.forms.application_member import *
from atat.forms.data import ENV_ROLES


def test_environment_form():
    form_data = {
        "environment_id": str(uuid.uuid4()),
        "environment_name": "testing",
        "role": ENV_ROLES[0][0],
        "disabled": True,
    }
    form = EnvironmentForm(data=form_data)
    assert form.validate()


def test_environment_form_default_no_access():
    env_id = str(uuid.uuid4())
    form_data = {"environment_id": env_id, "environment_name": "testing"}
    form = EnvironmentForm(data=form_data)

    assert form.validate()
    assert form.data == {
        "environment_id": env_id,
        "environment_name": "testing",
        "role": None,
        "disabled": False,
    }


def test_environment_form_invalid():
    form_data = {
        "environment_id": str(uuid.uuid4()),
        "environment_name": "testing",
        "role": "not a real choice",
    }
    form = EnvironmentForm(data=form_data)
    assert not form.validate()


def test_update_member_form():
    form_data = {
        "perms_team_mgmt": True,
        "perms_env_mgmt": False,
    }
    form = UpdateMemberForm(data=form_data)
    assert form.validate()
    assert form.perms_team_mgmt.data
    assert not form.perms_env_mgmt.data
