import pytest
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from atat.debug import debug_tools_bar


def test_debug_tools_bar():
    app2 = Flask(__name__)
    app2.config["DEV_DEBUG_TOOL"] = "True"
    app2.config["SECRET_KEY"] = "xxx"

    # Make sure bar is not set up on not valid ENVs
    toolbar1 = debug_tools_bar(app2, "prod")
    assert toolbar1 is None, "Toolbar should not be available on prod"
    toolbar1 = debug_tools_bar(app2, "bla")
    assert toolbar1 is None, "Toolbar should not be available on this env"
    toolbar1 = debug_tools_bar(app2, "")
    assert toolbar1 is None, "Toolbar should not be available on this env"

    # Make Sure it works in a valid ENV
    toolbar1 = debug_tools_bar(app2, "development")
    assert isinstance(
        toolbar1, DebugToolbarExtension
    ), "Toolbar is not available on development"
