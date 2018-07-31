from urllib.request import urlopen
import csv

# Add root project dir to the python path
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from atst.app import make_deps, make_config
from atst.domain.pe_numbers import PENumbers


def get_pe_numbers(url):
    response = urlopen(url)
    t = response.read().decode("utf-8")
    return list(csv.reader(t.split("\r\n")))

def make_pe_number_repo(config):
    deps = make_deps(config)
    db = deps["db_session"]
    return PENumbers(db)

if __name__ == "__main__":
    config = make_config()
    url = config["default"]['PE_NUMBER_CSV_URL']
    print("Fetching PE numbers from {}".format(url))
    pe_numbers = get_pe_numbers(url)
    print("Inserting {} PE numbers".format(len(pe_numbers)))
    pe_numbers_repo = make_pe_number_repo(config)
    pe_numbers_repo.create_many(pe_numbers)
