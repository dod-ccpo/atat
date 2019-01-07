import pytest

from atst.domain.task_orders import TaskOrders, TaskOrderError
from atst.domain.exceptions import UnauthorizedError

from atst.models.task_order import TaskOrder

from tests.factories import (
    TaskOrderFactory,
    UserFactory,
    PortfolioRoleFactory,
    PortfolioFactory,
)


def test_section_completion_status_when_complete():
    task_order = TaskOrderFactory.create()

    for section in TaskOrders.SECTIONS:
        assert TaskOrders.section_completion_status(task_order, section) == "complete"


def test_section_completion_status_when_draft():
    task_order = TaskOrderFactory.create()

    task_order.ko_first_name = None
    task_order.clin_01 = ""
    task_order.scope = None

    for section in TaskOrders.SECTIONS:
        assert TaskOrders.section_completion_status(task_order, section) == "draft"


def test_section_completion_status_when_incomplete():
    task_order = TaskOrder()

    for section in TaskOrders.SECTIONS:
        assert TaskOrders.section_completion_status(task_order, section) == "incomplete"


def test_all_sections_complete():
    task_order = TaskOrderFactory.create()
    assert TaskOrders.all_sections_complete(task_order)

    task_order.scope = None
    assert not TaskOrders.all_sections_complete(task_order)


def test_add_officer():
    task_order = TaskOrderFactory.create()
    ko = UserFactory.create()
    owner = task_order.portfolio.owner
    TaskOrders.add_officer(owner, task_order, "contracting_officer", ko.to_dictionary())

    assert task_order.contracting_officer == ko
    portfolio_users = [ws_role.user for ws_role in task_order.portfolio.members]
    assert ko in portfolio_users


def test_add_officer_with_nonexistent_role():
    task_order = TaskOrderFactory.create()
    ko = UserFactory.create()
    owner = task_order.portfolio.owner
    with pytest.raises(TaskOrderError):
        TaskOrders.add_officer(owner, task_order, "pilot", ko.to_dictionary())


def test_add_officer_who_is_already_portfolio_member():
    task_order = TaskOrderFactory.create()
    owner = task_order.portfolio.owner
    TaskOrders.add_officer(
        owner, task_order, "contracting_officer", owner.to_dictionary()
    )

    assert task_order.contracting_officer == owner
    member = task_order.portfolio.members[0]
    assert member.user == owner and member.role_name == "owner"


def test_task_order_access():
    creator = UserFactory.create()
    member = UserFactory.create()
    rando = UserFactory.create()
    officer = UserFactory.create()

    def check_access(can, cannot, method_name, method_args):
        method = getattr(TaskOrders, method_name)

        for user in can:
            assert method(user, *method_args)

        for user in cannot:
            with pytest.raises(UnauthorizedError):
                method(user, *method_args)

    portfolio = PortfolioFactory.create(owner=creator)
    task_order = TaskOrderFactory.create(creator=creator, portfolio=portfolio)
    PortfolioRoleFactory.create(user=member, portfolio=task_order.portfolio)
    TaskOrders.add_officer(
        creator, task_order, "contracting_officer", officer.to_dictionary()
    )

    check_access([creator, officer], [member, rando], "get", [task_order.id])
    check_access([creator], [officer, member, rando], "create", [portfolio])
    check_access([creator, officer], [member, rando], "update", [task_order])
    check_access(
        [creator],
        [officer, member, rando],
        "add_officer",
        [task_order, "contracting_officer", rando.to_dictionary()],
    )
