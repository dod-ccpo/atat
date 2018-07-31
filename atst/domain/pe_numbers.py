from sqlalchemy.dialects.postgresql import insert

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

    def create_many(self, list_of_pe_numbers):
        stmt = insert(PENumber).values(list_of_pe_numbers)
        do_update = stmt.on_conflict_do_update(
            index_elements=["number"],
            set_=dict(description=stmt.excluded.description)
        )
        self.db_session.execute(do_update)
        self.db_session.commit()
