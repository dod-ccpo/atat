from flask import current_app
from atat.domain.csp.cloud.models import (
    ReportingCSPPayload,
    CostManagementQueryCSPResult,
)
from atat.domain.csp.reports import prepare_azure_reporting_data
import pendulum


class Reports:
    @classmethod
    def expired_task_orders(cls, portfolio):
        return [
            task_order for task_order in portfolio.task_orders if task_order.is_expired
        ]

    @classmethod
    def get_portfolio_spending(cls, portfolio):
        # TODO: Extend this function to make from_date and to_date configurable
        from_date = pendulum.now().subtract(years=1).add(days=1).format("YYYY-MM-DD")
        to_date = pendulum.now().format("YYYY-MM-DD")
        rows = []

        if portfolio.csp_data:
            payload = ReportingCSPPayload(
                from_date=from_date, to_date=to_date, **portfolio.csp_data
            )
            response: CostManagementQueryCSPResult = current_app.csp.cloud.get_reporting_data(
                payload
            )
            rows = response.properties.rows

        return prepare_azure_reporting_data(rows)
