import json
import logging

from atat.models import Portfolio
from . import db

def get_portfolios():
    pfs = db._get_session().query(Portfolio).all()
    logging.info(f"Found {len(pfs)} Portfolio(s).")
    return json.dumps(pfs, cls=PortfolioEncoder)


class PortfolioEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Portfolio):
            return {
                "id": obj.id.hex,
                "name": obj.name,
                "description": obj.description
            }
        return json.JSONEncoder.default(self, obj)
