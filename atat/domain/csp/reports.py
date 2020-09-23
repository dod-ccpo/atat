import json
from decimal import Decimal

import pendulum


def load_fixture_data():
    with open("fixtures/fixture_spend_data.json") as json_file:
        return json.load(json_file)


class MockReportingProvider:
    FIXTURE_SPEND_DATA = load_fixture_data()


def prepare_azure_reporting_data(rows: list):
    """
    Returns a dict representing invoiced and estimated funds for a portfolio given
    a list of rows from CostManagementQueryCSPResult.properties.rows
    {
        invoiced: Decimal,
        estimated: Decimal
    }
    """

    estimated = []
    while rows:
        if pendulum.parse(rows[-1][1]) >= pendulum.now(tz="UTC").start_of("month"):
            estimated.append(rows.pop())
        else:
            break

    return dict(
        invoiced=Decimal(sum([row[0] for row in rows])),
        estimated=Decimal(sum([row[0] for row in estimated])),
    )
