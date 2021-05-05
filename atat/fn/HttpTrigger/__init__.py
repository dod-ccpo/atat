import logging

import azure.functions as func
import atat.fn.shared as shared

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return func.HttpResponse(body=shared.get_portfolios(), mimetype='application/json')

