import pendulum
from flask import current_app

from atat.domain.csp.cloud.models import (
    CostManagementQueryCSPPayload,
    CostManagementQueryCSPResult,
)
from atat.domain.csp.reports import prepare_azure_reporting_data


class Reports:
    @classmethod
    def expired_task_orders(cls, portfolio):
        return [
            task_order for task_order in portfolio.task_orders if task_order.is_expired
        ]

    @classmethod
    def get_portfolio_spending(cls, portfolio):
        # TODO: Extend this function to make from_date and to_date configurable
        from_date = (
            pendulum.now(tz="UTC").subtract(years=1).add(days=1).format("YYYY-MM-DD")
        )
        to_date = pendulum.now(tz="UTC").format("YYYY-MM-DD")
        rows = []
        if portfolio.is_provisioned:
            payload = CostManagementQueryCSPPayload(
                from_date=from_date, to_date=to_date, **portfolio.csp_data
            )
            response: CostManagementQueryCSPResult = current_app.csp.cloud.get_reporting_data(
                payload
            )
            rows = response.properties.rows

        return prepare_azure_reporting_data(rows)
