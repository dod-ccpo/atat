import pytest

from atat.domain.exceptions import NotFoundError
from atat.domain.permission_sets import PermissionSets
from atat.utils import first_or_none


def test_get_all():
    roles = PermissionSets.get_all()
    assert roles


def test_get_existing_permission_set():
    role = PermissionSets.get("portfolio_poc")
    assert role.name == "portfolio_poc"


def test_get_nonexistent_permission_set():
    with pytest.raises(NotFoundError):
        PermissionSets.get("nonexistent")


def test_get_many():
    perms_sets = PermissionSets.get_many(
        [PermissionSets.VIEW_PORTFOLIO_FUNDING, PermissionSets.EDIT_PORTFOLIO_FUNDING]
    )
    assert len(perms_sets) == 2
    assert first_or_none(
        lambda p: p.name == PermissionSets.VIEW_PORTFOLIO_FUNDING, perms_sets
    )
    assert first_or_none(
        lambda p: p.name == PermissionSets.EDIT_PORTFOLIO_FUNDING, perms_sets
    )


def test_get_many_nonexistent():
    with pytest.raises(NotFoundError):
        PermissionSets.get_many(["nonexistent", "not real"])
