import pytest
from flask import url_for

from atst.domain.task_orders import TaskOrders
from atst.routes.task_orders.new import ShowTaskOrderWorkflow, UpdateTaskOrderWorkflow

from tests.factories import UserFactory, TaskOrderFactory, PortfolioFactory


def test_new_task_order(client, user_session):
    creator = UserFactory.create()
    user_session()
    response = client.get(url_for("task_orders.new", screen=1))
    assert response.status_code == 200


def post_to_task_order_step(client, data, screen, task_order_id=None):
    return client.post(
        url_for("task_orders.update", screen=screen, task_order_id=task_order_id),
        data=data,
        follow_redirects=False,
    )


def slice_data_for_section(task_order_data, section):
    if section in TaskOrders.SECTIONS.keys():
        form = TaskOrders.SECTIONS[section]()

        form_fields = {}

        for attr in form.data:
            if attr in task_order_data.keys():
                _a = task_order_data[attr]
                if _a.__class__.__name__ == "date":
                    _a = _a.strftime("%m/%d/%Y")

                form_fields[attr] = _a

        return form_fields


def serialize_dates(data):
    if not data:
        return data

    dates = {
        k: v.strftime("%m/%d/%Y") for k, v in data.items() if hasattr(v, "strftime")
    }

    data.update(dates)

    return data


# TODO: this test will need to be more complicated when we add validation to
# the forms
def test_create_new_task_order(client, user_session):
    creator = UserFactory.create()
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    app_info_data = slice_data_for_section(task_order_data, "app_info")
    portfolio_name = "Mos Eisley"
    app_info_data["portfolio_name"] = portfolio_name

    response = client.post(
        url_for("task_orders.update", screen=1),
        data=app_info_data,
        follow_redirects=False,
    )
    assert url_for("task_orders.new", screen=2) in response.headers["Location"]

    created_task_order_id = response.headers["Location"].split("/")[-1]
    created_task_order = TaskOrders.get(creator, created_task_order_id)
    assert created_task_order.portfolio is not None
    assert created_task_order.portfolio.name == portfolio_name

    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    response = client.post(
        response.headers["Location"], data=funding_data, follow_redirects=False
    )
    assert url_for("task_orders.new", screen=3) in response.headers["Location"]

    oversight_data = slice_data_for_section(task_order_data, "oversight")
    response = client.post(
        response.headers["Location"], data=oversight_data, follow_redirects=False
    )
    assert url_for("task_orders.new", screen=4) in response.headers["Location"]


def test_create_new_task_order_for_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    creator = portfolio.owner
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    app_info_data = slice_data_for_section(task_order_data, "app_info")
    portfolio_name = "This is ignored for now"
    app_info_data["portfolio_name"] = portfolio_name

    response = client.post(
        url_for("task_orders.update", screen=1, portfolio_id=portfolio.id),
        data=app_info_data,
        follow_redirects=False,
    )
    assert url_for("task_orders.new", screen=2) in response.headers["Location"]

    created_task_order_id = response.headers["Location"].split("/")[-1]
    created_task_order = TaskOrders.get(creator, created_task_order_id)
    assert created_task_order.portfolio == portfolio


def test_task_order_form_shows_errors(client, user_session):
    to = task_order()
    creator = to.creator
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    funding_data.update({"clin_01": "one milllllion dollars"})

    response = client.post(
        url_for("task_orders.update", screen=2, task_order_id=to.id),
        data=funding_data,
        follow_redirects=False,
    )

    body = response.data.decode()
    assert "There were some errors" in body
    assert "Not a valid integer" in body


@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


def test_create_new_task_order_with_errors(client, user_session):
    user = UserFactory.create()
    to_data = TaskOrderFactory.dictionary()
    to_data["scope"] = None
    to_data["potfolio_name"] = "Hello"

    workflow = UpdateTaskOrderWorkflow(user, to_data)

    assert workflow.validate() is False
    assert "This field is required." in workflow.form.errors["scope"]


def test_show_task_order(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator)
    assert workflow.task_order is None
    another_workflow = ShowTaskOrderWorkflow(
        task_order.creator, task_order_id=task_order.id
    )
    assert another_workflow.task_order == task_order


def test_show_task_order_form_list_data():
    complexity = ["oconus", "tactical_edge"]
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(
        creator=user, portfolio=portfolio, complexity=complexity
    )
    workflow = ShowTaskOrderWorkflow(user, task_order_id=task_order.id)

    assert workflow.form.complexity.data == complexity


def test_show_task_order_form(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator)
    assert not workflow.form.data["app_migration"]
    another_workflow = ShowTaskOrderWorkflow(
        task_order.creator, task_order_id=task_order.id
    )
    assert (
        another_workflow.form.data["defense_component"] == task_order.defense_component
    )


def test_show_task_order_display_screen(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator, task_order_id=task_order.id)
    screens = workflow.display_screens
    # every form section is complete
    for i in range(2):
        assert screens[i]["complete"]
    # the review section is not
    assert not screens[3].get("complete")


def test_update_task_order_with_no_task_order():
    user = UserFactory.create()
    to_data = TaskOrderFactory.dictionary()
    workflow = UpdateTaskOrderWorkflow(user, to_data)
    assert workflow.task_order is None
    workflow.update()
    assert workflow.task_order
    assert workflow.task_order.scope == to_data["scope"]


def test_update_task_order_with_existing_task_order(task_order):
    to_data = serialize_dates(TaskOrderFactory.dictionary())
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, screen=2, task_order_id=task_order.id
    )
    assert workflow.task_order.start_date != to_data["start_date"]
    workflow.update()
    assert workflow.task_order.start_date.strftime("%m/%d/%Y") == to_data["start_date"]


def test_other_text_not_saved_if_other_not_checked(task_order):
    to_data = {
        **TaskOrderFactory.dictionary(),
        "complexity": ["conus"],
        "complexity_other": "quite complex",
    }
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, task_order_id=task_order.id
    )
    workflow.update()
    assert not workflow.task_order.complexity_other


def test_cor_data_set_to_user_data_if_am_cor_is_checked(task_order):
    to_data = {**task_order.to_dictionary(), "am_cor": True}
    workflow = UpdateTaskOrderWorkflow(task_order.creator, to_data, 3, task_order.id)
    workflow.update()
    assert task_order.cor_dod_id == task_order.creator.dod_id


def test_invite_officers_to_task_order(task_order, queue):
    to_data = {
        **TaskOrderFactory.dictionary(),
        "ko_invite": True,
        "cor_invite": True,
        "so_invite": True,
    }
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, screen=3, task_order_id=task_order.id
    )
    workflow.update()
    portfolio = task_order.portfolio
    # owner and three officers are portfolio members
    assert len(portfolio.members) == 4
    roles = [member.role.name for member in portfolio.members]
    # officers exist in roles
    assert roles.count("officer") == 3
    # email invitations are enqueued
    assert len(queue.get_queue()) == 3
    # task order has relationship to user for each officer role
    assert task_order.contracting_officer.dod_id == to_data["ko_dod_id"]
    assert task_order.contracting_officer_representative.dod_id == to_data["cor_dod_id"]
    assert task_order.security_officer.dod_id == to_data["so_dod_id"]


def test_add_officer_but_do_not_invite(task_order, queue):
    to_data = {
        **TaskOrderFactory.dictionary(),
        "ko_invite": False,
        "cor_invite": False,
        "so_invite": False,
    }
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, screen=3, task_order_id=task_order.id
    )
    workflow.update()
    portfolio = task_order.portfolio
    # owner is only portfolio member
    assert len(portfolio.members) == 1
    # no invitations are enqueued
    assert len(queue.get_queue()) == 0


def test_update_does_not_resend_invitation():
    user = UserFactory.create()
    contracting_officer = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(
        creator=user,
        portfolio=portfolio,
        ko_first_name=contracting_officer.first_name,
        ko_last_name=contracting_officer.last_name,
        ko_dod_id=contracting_officer.dod_id,
    )
    to_data = {**task_order.to_dictionary(), "ko_invite": True}
    workflow = UpdateTaskOrderWorkflow(
        user, to_data, screen=3, task_order_id=task_order.id
    )
    for i in range(2):
        workflow.update()
    assert len(contracting_officer.invitations) == 1


def test_review_task_order_form(client, user_session, task_order):
    user_session(task_order.creator)

    for idx, section in enumerate(TaskOrders.SECTIONS):
        response = client.get(
            url_for("task_orders.new", screen=idx + 1, task_order_id=task_order.id)
        )
        assert response.status_code == 200
