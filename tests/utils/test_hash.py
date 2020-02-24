import random
import re
import string

from atat.utils import sha256_hex


def test_sha256_hex():
    sample = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=random.randrange(200))
    )
    hashed = sha256_hex(sample)
    assert re.match("^[a-zA-Z0-9]+$", hashed)
    assert len(hashed) == 64
    hashed_again = sha256_hex(sample)
    assert hashed == hashed_again
