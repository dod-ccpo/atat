from decimal import Decimal

import pendulum
import pytest

from tests.factories import (
    ApplicationFactory,
    CLINFactory,
    PortfolioFactory,
    TaskOrderFactory,
    random_future_date,
    random_past_date,
)


@pytest.fixture(scope="function")
def upcoming_task_order():
    return dict(
        signed_at=pendulum.today(tz="UTC").subtract(days=3),
        create_clins=[
            dict(
                start_date=pendulum.today(tz="UTC").add(days=2),
                end_date=pendulum.today(tz="UTC").add(days=3),
                obligated_amount=Decimal(700.0),
            )
        ],
    )


@pytest.fixture(scope="function")
def current_task_order():
    return dict(
        signed_at=pendulum.today(tz="UTC").subtract(days=3),
        create_clins=[
            dict(
                start_date=pendulum.today(tz="UTC").subtract(days=1),
                end_date=pendulum.today(tz="UTC").add(days=1),
                obligated_amount=Decimal(1000.0),
            )
        ],
    )


@pytest.fixture(scope="function")
def past_task_order():
    return dict(
        signed_at=pendulum.today(tz="UTC").subtract(days=3),
        create_clins=[
            dict(
                start_date=pendulum.today(tz="UTC").subtract(days=3),
                end_date=pendulum.today(tz="UTC").subtract(days=2),
                obligated_amount=Decimal(500.0),
            )
        ],
    )


def test_portfolio_applications_excludes_deleted():
    portfolio = PortfolioFactory.create()
    app = ApplicationFactory.create(portfolio=portfolio)
    ApplicationFactory.create(portfolio=portfolio, deleted=True)
    assert len(portfolio.applications) == 1
    assert portfolio.applications[0].id == app.id


def test_funding_duration(session):
    # portfolio with active task orders
    portfolio = PortfolioFactory()

    funding_start_date = random_past_date()
    funding_end_date = random_future_date(year_min=2)

    TaskOrderFactory.create(
        signed_at=random_past_date(),
        portfolio=portfolio,
        create_clins=[
            {
                "start_date": funding_start_date,
                "end_date": random_future_date(year_max=1),
            }
        ],
    )
    TaskOrderFactory.create(
        portfolio=portfolio,
        signed_at=random_past_date(),
        create_clins=[
            {"start_date": pendulum.now(tz="UTC"), "end_date": funding_end_date,}
        ],
    )

    assert portfolio.funding_duration == (funding_start_date, funding_end_date)

    # empty portfolio
    empty_portfolio = PortfolioFactory()
    assert empty_portfolio.funding_duration == (None, None)


def test_days_remaining(session):
    # portfolio with task orders
    funding_end_date = random_future_date(year_min=2)
    portfolio = PortfolioFactory()
    TaskOrderFactory.create(
        portfolio=portfolio,
        signed_at=random_past_date(),
        create_clins=[{"end_date": funding_end_date}],
    )

    assert (
        portfolio.days_to_funding_expiration
        == (funding_end_date - pendulum.today(tz="UTC")).days
    )

    # empty portfolio
    empty_portfolio = PortfolioFactory()
    assert empty_portfolio.days_to_funding_expiration == 0


def test_active_task_orders(session):
    portfolio = PortfolioFactory()
    TaskOrderFactory.create(
        portfolio=portfolio,
        signed_at=random_past_date(),
        create_clins=[
            {
                "start_date": pendulum.date(2019, 1, 1),
                "end_date": pendulum.date(2019, 10, 31),
            }
        ],
    )
    TaskOrderFactory.create(
        portfolio=portfolio, signed_at=random_past_date(), clins=[CLINFactory.create()]
    )
    assert len(portfolio.active_task_orders) == 1


class TestCurrentObligatedFunds:
    """
    Tests the current_obligated_funds property
    """

    def test_no_task_orders(self):
        portfolio = PortfolioFactory()
        assert portfolio.total_obligated_funds == Decimal(0)

    def test_with_current(self, current_task_order):
        portfolio = PortfolioFactory(
            task_orders=[current_task_order, current_task_order]
        )
        assert portfolio.total_obligated_funds == Decimal(2000.0)

    def test_with_others(
        self, past_task_order, current_task_order, upcoming_task_order
    ):
        portfolio = PortfolioFactory(
            task_orders=[past_task_order, current_task_order, upcoming_task_order,]
        )
        # Only sums the current task order
        assert portfolio.total_obligated_funds == Decimal(1000.0)


class TestUpcomingObligatedFunds:
    """
    Tests the upcoming_obligated_funds property
    """

    def test_no_task_orders(self):
        portfolio = PortfolioFactory()
        assert portfolio.upcoming_obligated_funds == Decimal(0)

    def test_with_upcoming(self, upcoming_task_order):
        portfolio = PortfolioFactory(
            task_orders=[upcoming_task_order, upcoming_task_order]
        )
        assert portfolio.upcoming_obligated_funds == Decimal(1400.0)

    def test_with_others(
        self, past_task_order, current_task_order, upcoming_task_order
    ):
        portfolio = PortfolioFactory(
            task_orders=[past_task_order, current_task_order, upcoming_task_order]
        )
        # Only sums the upcoming task order
        assert portfolio.upcoming_obligated_funds == Decimal(700.0)


class TestInitialClinDict:
    def test_formats_dict_correctly(self):
        portfolio = PortfolioFactory()
        task_order = TaskOrderFactory(
            portfolio=portfolio,
            number="1234567890123",
            signed_at=pendulum.now(tz="UTC"),
        )
        clin = CLINFactory(task_order=task_order)
        initial_clin = portfolio.initial_clin_dict

        assert initial_clin["initial_clin_amount"] == clin.obligated_amount
        assert initial_clin["initial_clin_start_date"] == clin.start_date.strftime(
            "%Y/%m/%d"
        )
        assert initial_clin["initial_clin_end_date"] == clin.end_date.strftime(
            "%Y/%m/%d"
        )
        assert initial_clin["initial_clin_type"] == clin.jedi_clin_number
        assert initial_clin["initial_clin_number"] == clin.number
        assert initial_clin["initial_task_order_id"] == task_order.number

    def test_no_valid_clins(self):
        portfolio = PortfolioFactory()
        assert portfolio.initial_clin_dict == {}

    def test_picks_the_initial_clin(self):
        yesterday = pendulum.now(tz="UTC").subtract(days=1).date()
        tomorrow = pendulum.now(tz="UTC").add(days=1).date()
        portfolio = PortfolioFactory(
            task_orders=[
                {
                    "signed_at": pendulum.now(tz="UTC"),
                    "create_clins": [
                        {
                            "number": "0001",
                            "start_date": yesterday.subtract(days=1),
                            "end_date": yesterday,
                        },
                        {
                            "number": "1001",
                            "start_date": yesterday,
                            "end_date": tomorrow,
                        },
                        {
                            "number": "0002",
                            "start_date": yesterday,
                            "end_date": tomorrow,
                        },
                    ],
                },
                {"create_clins": [{"number": "0003"}]},
            ],
        )
        assert portfolio.initial_clin_dict["initial_clin_number"] == "1001"


class Test_tenant_id:
    def test_tenant_id(self):
        portfolio = PortfolioFactory.create(csp_data={"tenant_id": "123"})
        assert portfolio.tenant_id == "123"

    def test_no_csp_data(self):
        portfolio = PortfolioFactory.create(csp_data=None)
        assert portfolio.tenant_id is None

    def test_no_tenant_id(self):
        portfolio = PortfolioFactory.create(csp_data={})
        assert portfolio.tenant_id is None
