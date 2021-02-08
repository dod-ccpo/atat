from flask_debugtoolbar import DebugToolbarExtension


def debug_tools_bar(app, ENV):
    """
    Set debuger tool bar
    toolbar factory type DebugToolbarExtension
    """
    toolbar = None

    # check if it is a development valid branch.
    IS_DEVELOPMENT = ["dev", "development"].__contains__(ENV)
    # is dev debug tool true
    IS_DEV_TOOL = str(app.config["DEV_DEBUG_TOOL"]).lower() == "true"

    if IS_DEVELOPMENT and IS_DEV_TOOL:
        # The toolbar is only enabled in debug mode
        app.debug = True
        # This set the toolbar factory instance
        toolbar = DebugToolbarExtension(app)

    return toolbar
