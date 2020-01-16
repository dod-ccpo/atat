import pytest
from flask import url_for, get_flashed_messages
from datetime import timedelta, date
from uuid import uuid4

from atst.domain.task_orders import TaskOrders
from atst.models.task_order import Status as TaskOrderStatus
from atst.models import TaskOrder

from tests.factories import CLINFactory, PortfolioFactory, TaskOrderFactory, UserFactory
from tests.utils import captured_templates


def build_pdf_form_data(filename="sample.pdf", object_name=None):
    return {"pdf-filename": filename, "pdf-object_name": object_name or uuid4()}


@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    CLINFactory.create(task_order=task_order)

    return task_order


@pytest.fixture
def incomplete_to():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)

    return TaskOrderFactory.create(portfolio=portfolio)


@pytest.fixture
def completed_task_order():
    portfolio = PortfolioFactory.create()
    task_order = TaskOrderFactory.create(
        portfolio=portfolio,
        create_clins=[{"number": "1234567890123456789012345678901234567890123"}],
    )

    return task_order


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


def test_task_orders_form_step_one_add_pdf(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.get(
        url_for("task_orders.form_step_one_add_pdf", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_one_add_pdf(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.post(
        url_for("task_orders.submit_form_step_one_add_pdf", portfolio_id=portfolio.id),
        data=build_pdf_form_data(),
    )

    assert response.status_code == 302
    task_order = portfolio.task_orders[0]
    assert task_order.pdf.filename == "sample.pdf"


def test_task_orders_form_step_one_add_pdf_existing_to(
    client, user_session, task_order
):
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.form_step_one_add_pdf", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_one_add_pdf_existing_to(client, user_session):
    task_order = TaskOrderFactory.create()
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for(
            "task_orders.submit_form_step_one_add_pdf", task_order_id=task_order.id
        ),
        data=build_pdf_form_data(),
    )
    assert response.status_code == 302
    assert task_order.pdf.filename == "sample.pdf"


def test_task_orders_submit_form_step_one_add_pdf_delete_pdf(
    client, user_session, portfolio
):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    response = client.post(
        url_for(
            "task_orders.submit_form_step_one_add_pdf", task_order_id=task_order.id
        ),
        data=build_pdf_form_data(filename="", object_name=""),
    )
    assert task_order.pdf is None
    assert response.status_code == 302


def test_task_orders_submit_form_step_one_validates_filename(
    app, client, user_session, portfolio
):
    user_session(portfolio.owner)
    with captured_templates(app) as templates:
        client.post(
            url_for(
                "task_orders.submit_form_step_one_add_pdf", portfolio_id=portfolio.id
            ),
            data={"pdf-filename": "a" * 1024},
            follow_redirects=True,
        )

        _, context = templates[-1]

        assert "filename" in context["form"].pdf.errors


def test_task_orders_submit_form_step_one_validates_object_name(
    app, client, user_session, portfolio
):
    user_session(portfolio.owner)
    with captured_templates(app) as templates:
        client.post(
            url_for(
                "task_orders.submit_form_step_one_add_pdf", portfolio_id=portfolio.id
            ),
            data={"pdf-object_name": "a" * 41},
            follow_redirects=True,
        )

        _, context = templates[-1]

        assert "object_name" in context["form"].pdf.errors


def test_task_orders_form_step_two_add_number(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.form_step_two_add_number", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_two_add_number(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    form_data = {"number": "1234567890"}
    response = client.post(
        url_for(
            "task_orders.submit_form_step_two_add_number", task_order_id=task_order.id
        ),
        data=form_data,
    )

    assert response.status_code == 302
    assert task_order.number == "1234567890"


def test_task_orders_submit_form_step_two_enforces_unique_number(
    client, user_session, task_order, session
):
    number = "1234567890123"
    dupe_task_order = TaskOrderFactory.create(number=number)
    portfolio = task_order.portfolio
    user_session(task_order.portfolio.owner)
    form_data = {"number": number}
    session.begin_nested()
    response = client.post(
        url_for(
            "task_orders.submit_form_step_two_add_number", task_order_id=task_order.id
        ),
        data=form_data,
    )
    session.rollback()

    assert response.status_code == 400


def test_task_orders_submit_form_step_two_add_number_existing_to(
    client, user_session, task_order
):
    user_session(task_order.portfolio.owner)
    form_data = {"number": "0000000000"}
    original_number = task_order.number
    response = client.post(
        url_for(
            "task_orders.submit_form_step_two_add_number", task_order_id=task_order.id
        ),
        data=form_data,
    )
    assert response.status_code == 302
    assert task_order.number == "0000000000"
    assert task_order.number != original_number


def test_task_orders_form_step_three_add_clins(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.form_step_three_add_clins", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_three_add_clins(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    form_data = {
        "clins-0-jedi_clin_type": "JEDI_CLIN_1",
        "clins-0-number": "12312",
        "clins-0-start_date": "01/01/2020",
        "clins-0-end_date": "01/01/2021",
        "clins-0-obligated_amount": "5000",
        "clins-0-total_amount": "10000",
        "clins-1-jedi_clin_type": "JEDI_CLIN_1",
        "clins-1-number": "12312",
        "clins-1-start_date": "01/01/2020",
        "clins-1-end_date": "01/01/2021",
        "clins-1-obligated_amount": "5000",
        "clins-1-total_amount": "5000",
    }
    response = client.post(
        url_for(
            "task_orders.submit_form_step_three_add_clins", task_order_id=task_order.id
        ),
        data=form_data,
    )

    assert response.status_code == 302
    assert len(task_order.clins) == 2


def test_task_orders_submit_form_step_three_add_clins_existing_to(
    client, user_session, task_order
):
    clin_list = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": "01/01/2020",
            "end_date": "01/01/2021",
            "obligated_amount": "5000",
            "total_amount": "10000",
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": "01/01/2020",
            "end_date": "01/01/2021",
            "obligated_amount": "5000",
            "total_amount": "10000",
        },
    ]
    TaskOrders.create_clins(task_order.id, clin_list)
    assert len(task_order.clins) == 3

    user_session(task_order.portfolio.owner)
    form_data = {
        "clins-0-jedi_clin_type": "JEDI_CLIN_1",
        "clins-0-number": "12312",
        "clins-0-start_date": "01/01/2020",
        "clins-0-end_date": "01/01/2021",
        "clins-0-obligated_amount": "5000",
        "clins-0-total_amount": "10000",
    }
    response = client.post(
        url_for(
            "task_orders.submit_form_step_three_add_clins", task_order_id=task_order.id
        ),
        data=form_data,
    )

    assert response.status_code == 302
    assert len(task_order.clins) == 1


def test_task_orders_form_step_four_review(client, user_session, completed_task_order):
    user_session(completed_task_order.portfolio.owner)
    response = client.get(
        url_for(
            "task_orders.form_step_four_review", task_order_id=completed_task_order.id
        )
    )
    assert response.status_code == 200


def test_task_orders_form_step_four_review_incomplete_to(
    client, user_session, incomplete_to
):
    user_session(incomplete_to.portfolio.owner)
    response = client.get(
        url_for("task_orders.form_step_four_review", task_order_id=incomplete_to.id)
    )
    assert response.status_code == 404


def test_task_orders_form_step_five_confirm_signature(
    client, user_session, completed_task_order
):
    user_session(completed_task_order.portfolio.owner)
    response = client.get(
        url_for(
            "task_orders.form_step_five_confirm_signature",
            task_order_id=completed_task_order.id,
        )
    )
    assert response.status_code == 200


def test_task_orders_form_step_five_confirm_signature_incomplete_to(
    client, user_session, incomplete_to
):
    user_session(incomplete_to.portfolio.owner)
    response = client.get(
        url_for(
            "task_orders.form_step_five_confirm_signature",
            task_order_id=incomplete_to.id,
        )
    )
    assert response.status_code == 404


def test_task_orders_submit_task_order(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 302

    active_start_date = date.today() - timedelta(days=1)
    active_task_order = TaskOrderFactory(portfolio=task_order.portfolio)
    CLINFactory(task_order=active_task_order, start_date=active_start_date)
    assert active_task_order.status == TaskOrderStatus.UNSIGNED
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=active_task_order.id)
    )
    assert active_task_order.status == TaskOrderStatus.ACTIVE

    upcoming_start_date = date.today() + timedelta(days=1)
    upcoming_task_order = TaskOrderFactory(portfolio=task_order.portfolio)
    CLINFactory(task_order=upcoming_task_order, start_date=upcoming_start_date)
    assert upcoming_task_order.status == TaskOrderStatus.UNSIGNED
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=upcoming_task_order.id)
    )
    assert upcoming_task_order.status == TaskOrderStatus.UPCOMING


@pytest.mark.parametrize(
    "to_factory_args,expected_step",
    [
        ({"_pdf": None, "number": "", "clins": []}, "step_1"),
        ({"number": "", "clins": []}, "step_2"),
        ({"number": "1234567890123", "clins": []}, "step_3"),
        ({"number": "1234567890123", "create_clins": [{"number": 1}]}, "step_4"),
    ],
)
def test_task_orders_edit_redirects_to_latest_incomplete_step(
    client, user_session, portfolio, to_factory_args, expected_step
):
    task_order = TaskOrderFactory.create(portfolio=portfolio, **to_factory_args)
    user_session(portfolio.owner)

    response = client.get(url_for("task_orders.edit", task_order_id=task_order.id))

    assert expected_step in response.location


def test_can_cancel_edit_and_save_task_order(client, user_session, task_order, session):
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.cancel_edit", task_order_id=task_order.id, save=True),
        data={"number": "7896564324567"},
    )
    assert response.status_code == 302

    updated_task_order = session.query(TaskOrder).get(task_order.id)
    assert updated_task_order.number == "7896564324567"


def test_cancel_can_create_new_to(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.post(
        url_for("task_orders.cancel_edit", portfolio_id=portfolio.id),
        data={"number": "7643906432984"},
    )
    assert response.status_code == 302


def test_cancel_edit_causes_to_to_be_deleted(client, user_session, session):
    task_order = TaskOrderFactory.create()
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.cancel_edit", task_order_id=task_order.id, save=False),
        data={},
    )
    assert response.status_code == 302

    # TO should be deleted
    assert session.query(TaskOrder).get(task_order.id) is None


def test_cancel_edit_and_save_with_invalid_input_does_not_flash(
    app, client, user_session, session
):
    task_order = TaskOrderFactory.create()
    user_session(task_order.portfolio.owner)

    bad_data = {"clins-0-jedi_clin_type": "foo"}

    response = client.post(
        url_for("task_orders.cancel_edit", task_order_id=task_order.id, save=True),
        data=bad_data,
    )

    assert len(get_flashed_messages()) == 0


@pytest.mark.skip(reason="Reevaluate how form handles invalid data")
def test_task_orders_update_invalid_data(client, user_session, portfolio):
    user_session(portfolio.owner)
    num_task_orders = len(portfolio.task_orders)
    response = client.post(
        url_for("task_orders.update", portfolio_id=portfolio.id), data={"number": ""}
    )
    assert response.status_code == 400
    assert num_task_orders == len(portfolio.task_orders)
    assert "There were some errors" in response.data.decode()


@pytest.mark.skip(reason="Update after implementing errors on TO form")
def test_task_order_form_shows_errors(client, user_session, task_order):
    user_session(task_order.portfolio.owner)

    task_order_data = TaskOrderFactory.dictionary()
    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    funding_data.update({"clin_01": "one milllllion dollars"})

    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id),
        data=funding_data,
        follow_redirects=False,
    )

    body = response.data.decode()
    assert "There were some errors" in body
    assert "Not a valid decimal" in body
