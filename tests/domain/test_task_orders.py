import pytest

from atst.domain.task_orders import TaskOrders, TaskOrderError, DD254s
from atst.domain.exceptions import UnauthorizedError
from atst.models.attachment import Attachment

from tests.factories import (
    TaskOrderFactory,
    UserFactory,
    PortfolioRoleFactory,
    PortfolioFactory,
    DD254Factory,
)


def test_is_signed_by_ko():
    user = UserFactory.create()
    task_order = TaskOrderFactory.create(contracting_officer=user)

    assert not TaskOrders.is_signed_by_ko(task_order)

    TaskOrders.update(user, task_order, signer_dod_id=user.dod_id)

    assert TaskOrders.is_signed_by_ko(task_order)


def test_section_completion_status():
    dict_keys = [k for k in TaskOrders.SECTIONS.keys()]
    section = dict_keys[0]
    attrs = TaskOrders.SECTIONS[section].copy()
    attrs.remove("portfolio_name")
    task_order = TaskOrderFactory.create(**{k: None for k in attrs})
    leftover = attrs.pop()

    for attr in attrs:
        setattr(task_order, attr, "str12345")

    assert TaskOrders.section_completion_status(task_order, section) == "draft"

    setattr(task_order, leftover, "str12345")
    assert TaskOrders.section_completion_status(task_order, section) == "complete"


def test_all_sections_complete():
    task_order = TaskOrderFactory.create()
    attachment = Attachment(
        filename="sample_attachment",
        object_name="sample",
        resource="task_order",
        resource_id=task_order.id,
    )

    custom_attrs = {"csp_estimate": attachment}
    for attr_list in TaskOrders.SECTIONS.values():
        for attr in attr_list:
            if not getattr(task_order, attr):
                setattr(task_order, attr, custom_attrs.get(attr, "str12345"))

    task_order.scope = None
    assert not TaskOrders.all_sections_complete(task_order)
    task_order.scope = "str12345"
    assert TaskOrders.all_sections_complete(task_order)


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


def test_dd254_complete():
    finished = DD254Factory.create()
    unfinished = DD254Factory.create(certifying_official=None)

    assert DD254s.is_complete(finished)
    assert not DD254s.is_complete(unfinished)
