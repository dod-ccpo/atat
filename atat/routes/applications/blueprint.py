from flask import Blueprint

from atat.utils.context_processors import portfolio as portfolio_context_processor

applications_bp = Blueprint("applications", __name__)
applications_bp.context_processor(portfolio_context_processor)
