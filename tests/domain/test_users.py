from uuid import uuid4

import pytest

from atat.domain.exceptions import AlreadyExistsError, NotFoundError, UnauthorizedError
from atat.domain.users import Users
from atat.utils import pick
from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    PortfolioFactory,
    UserFactory,
)

DOD_ID = "my_dod_id"
REQUIRED_KWARGS = {"first_name": "Luke", "last_name": "Skywalker"}


def test_create_user():
    user = Users.create(DOD_ID, **REQUIRED_KWARGS)
    assert user.dod_id == DOD_ID


def test_create_user_with_existing_email():
    Users.create(DOD_ID, email="thisusersemail@usersRus.com", **REQUIRED_KWARGS)
    with pytest.raises(AlreadyExistsError):
        Users.create(DOD_ID, email="thisusersemail@usersRus.com")


def test_create_user_with_nonexistent_permission_set():
    with pytest.raises(NotFoundError):
        Users.create(DOD_ID, permission_sets=["nonexistent"], **REQUIRED_KWARGS)


def test_get_or_create_nonexistent_user():
    user = Users.get_or_create_by_dod_id(DOD_ID, **REQUIRED_KWARGS)
    assert user.dod_id == DOD_ID


def test_get_or_create_existing_user():
    fact_user = UserFactory.create()
    user = Users.get_or_create_by_dod_id(
        fact_user.dod_id,
        **pick(["first_name", "last_name"], fact_user.to_dictionary()),
    )
    assert user == fact_user


def test_get_user():
    new_user = UserFactory.create()
    user = Users.get(new_user.id)
    assert user.id == new_user.id


def test_get_nonexistent_user():
    with pytest.raises(NotFoundError):
        Users.get(uuid4())


def test_get_user_by_dod_id():
    new_user = UserFactory.create()
    user = Users.get_by_dod_id(new_user.dod_id)
    assert user == new_user


def test_update_user():
    new_user = UserFactory.create()
    updated_user = Users.update(new_user, {"first_name": "Jabba"})
    assert updated_user.first_name == "Jabba"


def test_update_user_with_dod_id():
    new_user = UserFactory.create()
    with pytest.raises(UnauthorizedError) as excinfo:
        Users.update(new_user, {"dod_id": "1234567890"})

    assert "dod_id" in str(excinfo.value)


def test_update_user_with_last_login():
    new_user = UserFactory.create()
    Users.update_last_login(new_user)
    last_login = new_user.last_login
    Users.update_last_login(new_user)
    assert new_user.last_login > last_login


def test_get_ccpo_users():
    ccpo_1 = UserFactory.create_ccpo()
    ccpo_2 = UserFactory.create_ccpo()
    rando = UserFactory.create()

    ccpo_users = Users.get_ccpo_users()
    assert ccpo_1 in ccpo_users
    assert ccpo_2 in ccpo_users
    assert rando not in ccpo_users


def test_give_ccpo_perms():
    rando = UserFactory.create()
    Users.give_ccpo_perms(rando)
    ccpo_users = Users.get_ccpo_users()
    assert rando in ccpo_users


def test_revoke_ccpo_perms():
    ccpo = UserFactory.create_ccpo()
    Users.revoke_ccpo_perms(ccpo)
    ccpo_users = Users.get_ccpo_users()
    assert ccpo not in ccpo_users
