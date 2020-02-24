#! .venv/bin/python

import os
import sys
import subprocess
from subprocess import check_output

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atat.utils.localization import all_keys

for key in all_keys():
    try:
        check_output("git grep -q '{}'".format(key), shell=True)
    except Exception:
        print(key)
