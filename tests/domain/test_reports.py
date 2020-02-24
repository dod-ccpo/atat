import pytest

from atat.domain.reports import Reports
from tests.factories import PortfolioFactory
from decimal import Decimal


@pytest.fixture(scope="function")
def portfolio():
    portfolio = PortfolioFactory.create()
    return portfolio


class TestGetPortfolioSpending:
    csp_data = {
        "tenant_id": "",
        "billing_profile_properties": {
            "invoice_sections": [{"invoice_section_id": "",}]
        },
    }

    def test_with_csp_data(self, portfolio):
        portfolio.csp_data = self.csp_data
        data = Reports.get_portfolio_spending(portfolio)
        assert data["invoiced"] == Decimal(1551.0)
        assert data["estimated"] == Decimal(500.0)

    def test_without_csp_data(self, portfolio):
        data = Reports.get_portfolio_spending(portfolio)
        assert data["invoiced"] == Decimal(0)
        assert data["estimated"] == Decimal(0)
