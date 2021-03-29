from decimal import Decimal

from atat.domain.reports import Reports
from tests.factories import PortfolioFactory


class TestGetPortfolioSpending:
    csp_data = {
        "tenant_id": "",
        "billing_profile_properties": {
            "invoice_sections": [{"invoice_section_id": "",}]
        },
    }

    def test_with_completed_state_machine(self):
        portfolio = PortfolioFactory.create(state="COMPLETED")
        portfolio.csp_data = self.csp_data
        data = Reports.get_portfolio_spending(portfolio)
        assert data["invoiced"] == Decimal(1551.0)
        assert data["estimated"] == Decimal(500.0)

    def test_not_completed_state_machine(self):
        portfolio = PortfolioFactory.create(state="UNSTARTED")
        portfolio.csp_data = self.csp_data
        data = Reports.get_portfolio_spending(portfolio)
        assert data["invoiced"] == Decimal(0)
        assert data["estimated"] == Decimal(0)

    def test_with_no_state_machine(self):
        portfolio = PortfolioFactory.create()
        data = Reports.get_portfolio_spending(portfolio)
        assert data["invoiced"] == Decimal(0)
        assert data["estimated"] == Decimal(0)
