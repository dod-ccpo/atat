from atst.models.pe_number import PENumber
from .exceptions import NotFoundError


class PENumbers(object):

    def __init__(self, db_session):
        self.db_session = db_session

    def get(self, number):
        pe_number = self.db_session.query(PENumber).get(number)
        if not pe_number:
            raise NotFoundError("pe_number")

        return pe_number
