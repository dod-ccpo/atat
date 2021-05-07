import logging

import azure.functions as func
from shared import portfolios_api #(absolute)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return func.HttpResponse(body=portfolios_api.get_portfolios(), mimetype='application/json')

