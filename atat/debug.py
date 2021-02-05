from flask_debugtoolbar import DebugToolbarExtension


def debug_tools_bar(app):
    """
    Set debuger tool bar
    toolbar factory type DebugToolbarExtension
    """
    # The toolbar is only enabled in debug mode
    app.debug = True
    # This set the toolbar factory instance
    toolbar = DebugToolbarExtension(app)
    return toolbar
