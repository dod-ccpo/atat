from urllib.request import urlopen
import csv

from sqlalchemy.dialects.postgresql import insert

# Add root project dir to the python path
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from atst.app import make_deps, make_config
from atst.models import PENumber


def get_pe_numbers(url):
    response = urlopen(url)
    t = response.read().decode("utf-8")
    return list(csv.reader(t.split("\r\n")))


def insert_pe_numbers(db, list_of_pe_numbers):
    stmt = insert(PENumber).values(list_of_pe_numbers)
    do_update = stmt.on_conflict_do_update(
        index_elements=["number"],
        set_=dict(description=stmt.excluded.description)
    )
    db.execute(do_update)
    db.commit()


if __name__ == "__main__":
    config = make_config()
    deps = make_deps(config)
    db = deps["db_session"]
    url = config["default"]['PE_NUMBER_CSV_URL']
    print("Fetching PE numbers from {}".format(url))
    pe_numbers = get_pe_numbers(url)
    print("Inserting {} PE numbers".format(len(pe_numbers)))
    insert_pe_numbers(db, pe_numbers)
