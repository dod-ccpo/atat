from atat.domain.csp.reports import prepare_azure_reporting_data
from tests.factories import PortfolioFactory
from decimal import Decimal
import pendulum


class TestPrepareAzureData:
    start_of_month = pendulum.today(tz="utc").start_of("month").replace(tzinfo=None)
    next_month = start_of_month.add(months=1).to_atom_string()
    this_month = start_of_month.to_atom_string()
    last_month = start_of_month.subtract(months=1).to_atom_string()
    two_months_ago = last_month = start_of_month.subtract(months=2).to_atom_string()

    def test_estimated_and_invoiced(self):
        rows = [
            [150.0, self.two_months_ago, "", "USD"],
            [100.0, self.last_month, "e0500a4qhw", "USD"],
            [50.0, self.this_month, "", "USD"],
            [50.0, self.next_month, "", "USD"],
        ]
        output = prepare_azure_reporting_data(rows)

        assert output.get("invoiced") == Decimal(250.0)
        assert output.get("estimated") == Decimal(100.0)

    def test_just_estimated(self):
        rows = [
            [100.0, self.this_month, "", "USD"],
        ]
        output = prepare_azure_reporting_data(rows)

        assert output.get("invoiced") == Decimal(0.0)
        assert output.get("estimated") == Decimal(100.0)

    def test_just_invoiced(self):
        rows = [
            [100.0, self.last_month, "", "USD"],
        ]
        output = prepare_azure_reporting_data(rows)

        assert output.get("invoiced") == Decimal(100.0)
        assert output.get("estimated") == Decimal(0.0)

    def test_no_rows(self):
        output = prepare_azure_reporting_data([])
        assert output.get("invoiced") == Decimal(0.0)
        assert output.get("estimated") == Decimal(0.0)
