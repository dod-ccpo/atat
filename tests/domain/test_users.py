import pytest
from uuid import uuid4, UUID

from atst.domain.users import Users
from atst.domain.exceptions import NotFoundError, AlreadyExistsError


@pytest.fixture()
def users_repo(db) -> Users:
    return Users(db)


@pytest.fixture(scope="function")
def user_id():
    return uuid4()


def test_create_user(users_repo, user_id):
    user = users_repo.create(user_id, "developer")
    assert user.id == user_id


def test_create_user_with_nonexistent_role(users_repo, user_id):
    with pytest.raises(NotFoundError):
        users_repo.create(user_id, "nonexistent")


def test_create_already_existing_user(users_repo, user_id):
    users_repo.create(user_id, "developer")
    with pytest.raises(AlreadyExistsError):
        users_repo.create(user_id, "developer")


def test_get_or_create_nonexistent_user(users_repo, user_id):
    user = users_repo.get_or_create(user_id, atat_role_name="developer")
    assert user.id == user_id


def test_get_or_create_existing_user(users_repo, user_id):
    users_repo.get_or_create(user_id, atat_role_name="developer")
    user = users_repo.get_or_create(user_id, atat_role_name="developer")
    assert user


def test_get_user(users_repo, user_id):
    users_repo.create(user_id, "developer")
    user = users_repo.get(user_id)
    assert user.id == user_id


def test_get_nonexistent_user(users_repo, user_id):
    users_repo.create(user_id, "developer")
    with pytest.raises(NotFoundError):
        users_repo.get(uuid4())


def test_update_user(users_repo, user_id):
    users_repo.create(user_id, "developer")
    updated_user = users_repo.update(user_id, "ccpo")

    assert updated_user.atat_role.name == "ccpo"


def test_update_nonexistent_user(users_repo, user_id):
    users_repo.create(user_id, "developer")
    with pytest.raises(NotFoundError):
        users_repo.update(uuid4(), "ccpo")


def test_update_existing_user_with_nonexistent_role(users_repo, user_id):
    users_repo.create(user_id, "developer")
    with pytest.raises(NotFoundError):
        users_repo.update(user_id, "nonexistent")
