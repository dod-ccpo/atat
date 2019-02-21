from flask import url_for
import pytest
from datetime import timedelta, date

from atst.domain.roles import Roles
from atst.domain.task_orders import TaskOrders
from atst.models.portfolio_role import Status as PortfolioStatus
from atst.utils.localization import translate

from tests.factories import (
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
    DD254Factory,
    random_future_date,
    random_past_date,
)
from tests.utils import captured_templates


class TestPortfolioFunding:
    def test_portfolio_with_no_task_orders(self, app, user_session):
        portfolio = PortfolioFactory.create()
        user_session(portfolio.owner)

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is None
            assert context["total_balance"] == 0
            assert context["pending_task_orders"] == []
            assert context["active_task_orders"] == []
            assert context["expired_task_orders"] == []

    def test_funded_portfolio(self, app, user_session):
        portfolio = PortfolioFactory.create()
        user_session(portfolio.owner)

        pending_to = TaskOrderFactory.create(portfolio=portfolio)
        active_to1 = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(),
            number="42",
        )
        active_to2 = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(),
            number="43",
        )
        end_date = (
            active_to1.end_date
            if active_to1.end_date > active_to2.end_date
            else active_to2.end_date
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is end_date
            assert context["total_balance"] == active_to1.budget + active_to2.budget

    def test_expiring_and_funded_portfolio(self, app, user_session):
        portfolio = PortfolioFactory.create()
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=(date.today() + timedelta(days=10)),
            number="42",
        )
        active_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(year_min=1, year_max=2),
            number="43",
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is active_to.end_date
            assert context["funded"] == True

    def test_expiring_and_unfunded_portfolio(self, app, user_session):
        portfolio = PortfolioFactory.create()
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=(date.today() + timedelta(days=10)),
            number="42",
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is expiring_to.end_date
            assert context["funded"] == False


class TestTaskOrderInvitations:
    def setup(self):
        self.portfolio = PortfolioFactory.create()
        self.task_order = TaskOrderFactory.create(portfolio=self.portfolio)

    def _post(self, client, updates):
        return client.post(
            url_for(
                "portfolios.edit_task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=self.task_order.id,
            ),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=updates,
        )

    def test_editing_with_partial_data(self, user_session, client):
        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-first_name": "Luke",
                "contracting_officer-last_name": "Skywalker",
                "security_officer-first_name": "Boba",
                "security_officer-last_name": "Fett",
            },
        )
        updated_task_order = TaskOrders.get(self.portfolio.owner, self.task_order.id)
        assert updated_task_order.ko_first_name == "Luke"
        assert updated_task_order.ko_last_name == "Skywalker"
        assert updated_task_order.so_first_name == "Boba"
        assert updated_task_order.so_last_name == "Fett"

    def test_editing_with_invalid_data(self, user_session, client):
        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-phone_number": "invalid input",
                "security_officer-first_name": "Boba",
                "security_officer-last_name": "Fett",
            },
        )

        assert "There were some errors" in response.data.decode()

        updated_task_order = TaskOrders.get(self.portfolio.owner, self.task_order.id)
        assert updated_task_order.so_first_name != "Boba"


def test_ko_can_view_task_order(client, user_session):
    portfolio = PortfolioFactory.create()
    ko = UserFactory.create()
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    user_session(ko)

    response = client.get(
        url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200
    assert translate("common.manage") in response.data.decode()

    TaskOrders.update(ko, task_order, clin_01=None)
    response = client.get(
        url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200
    assert translate("common.manage") not in response.data.decode()


def test_can_view_task_order_invitations_when_complete(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    response = client.get(
        url_for(
            "portfolios.task_order_invitations",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200


def test_cant_view_task_order_invitations_when_not_complete(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, clin_01=None)
    response = client.get(
        url_for(
            "portfolios.task_order_invitations",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 404


def test_ko_can_view_ko_review_page(client, user_session):
    portfolio = PortfolioFactory.create()
    ko = UserFactory.create()
    cor = UserFactory.create()

    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
    )
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=cor,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(
        portfolio=portfolio,
        contracting_officer=ko,
        contracting_officer_representative=cor,
    )
    request_url = url_for(
        "portfolios.ko_review", portfolio_id=portfolio.id, task_order_id=task_order.id
    )

    #
    # KO returns 200
    #
    user_session(ko)
    response = client.get(request_url)
    assert response.status_code == 200

    #
    # COR returns 200
    #
    user_session(cor)
    response = client.get(request_url)
    assert response.status_code == 200

    #
    # Random user raises UnauthorizedError
    #
    user_session(UserFactory.create())
    response = client.get(request_url)
    assert response.status_code == 404


def test_mo_redirected_to_build_page(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    response = client.get(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_cor_redirected_to_build_page(client, user_session):
    portfolio = PortfolioFactory.create()
    cor = UserFactory.create()
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=cor,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer_representative=cor
    )
    user_session(cor)
    response = client.get(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_submit_completed_ko_review_page_as_cor(client, user_session, pdf_upload):
    portfolio = PortfolioFactory.create()

    cor = UserFactory.create()

    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=cor,
        status=PortfolioStatus.ACTIVE,
    )

    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer_representative=cor
    )

    form_data = {
        "start_date": "02/10/2019",
        "end_date": "03/10/2019",
        "number": "1938745981",
        "loa": "0813458013405",
        "custom_clauses": "hi im a custom clause",
        "pdf": pdf_upload,
    }

    user_session(cor)

    response = client.post(
        url_for(
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        ),
        data=form_data,
    )

    assert task_order.pdf
    assert response.headers["Location"] == url_for(
        "portfolios.view_task_order",
        task_order_id=task_order.id,
        portfolio_id=portfolio.id,
        _external=True,
    )


def test_submit_completed_ko_review_page_as_ko(client, user_session, pdf_upload):
    portfolio = PortfolioFactory.create()

    ko = UserFactory.create()

    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
    )

    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    user_session(ko)

    form_data = {
        "start_date": "02/10/2019",
        "end_date": "03/10/2019",
        "number": "1938745981",
        "loa": "0813458013405",
        "custom_clauses": "hi im a custom clause",
        "pdf": pdf_upload,
    }

    response = client.post(
        url_for(
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        ),
        data=form_data,
    )
    assert task_order.pdf
    assert response.headers["Location"] == url_for(
        "task_orders.signature_requested", task_order_id=task_order.id, _external=True
    )


def test_so_review_page(app, client, user_session):
    portfolio = PortfolioFactory.create()
    so = UserFactory.create()
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=so,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)

    user_session(portfolio.owner)
    owner_response = client.get(
        url_for(
            "portfolios.so_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert owner_response.status_code == 404

    with captured_templates(app) as templates:
        user_session(so)
        so_response = app.test_client().get(
            url_for(
                "portfolios.so_review",
                portfolio_id=portfolio.id,
                task_order_id=task_order.id,
            )
        )
        _, context = templates[0]
        form = context["form"]
        co_name = form.certifying_official.data
        assert so_response.status_code == 200
        assert (
            task_order.so_first_name in co_name and task_order.so_last_name in co_name
        )


def test_submit_so_review(app, client, user_session):
    portfolio = PortfolioFactory.create()
    so = UserFactory.create()
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=so,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)
    dd_254_data = DD254Factory.dictionary()

    user_session(so)
    response = client.post(
        url_for(
            "portfolios.submit_so_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        ),
        data=dd_254_data,
    )
    expected_redirect = url_for(
        "portfolios.view_task_order",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
        _external=True,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == expected_redirect

    assert task_order.dd_254
    assert task_order.dd_254.certifying_official == dd_254_data["certifying_official"]
