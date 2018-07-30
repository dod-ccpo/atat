import pytest
from atst.domain.roles import Roles
from atst.domain.exceptions import NotFoundError


@pytest.fixture()
def roles_repo(db):
    return Roles(db)


def test_get_all_roles(roles_repo):
    roles = roles_repo.get_all()
    assert roles


def test_get_existing_role(roles_repo):
    role = roles_repo.get("developer")
    assert role.name == "developer"


def test_get_nonexistent_role(roles_repo):
    with pytest.raises(NotFoundError):
        roles_repo.get("nonexistent")
