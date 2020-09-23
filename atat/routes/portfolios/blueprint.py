from flask import Blueprint

from atat.utils.context_processors import portfolio as portfolio_context_processor

portfolios_bp = Blueprint("portfolios", __name__)
portfolios_bp.context_processor(portfolio_context_processor)
