from flask import Blueprint
from atat.utils.context_processors import portfolio as portfolio_context_processor

task_orders_bp = Blueprint("task_orders", __name__)
task_orders_bp.context_processor(portfolio_context_processor)
