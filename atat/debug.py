from flask_debugtoolbar import DebugToolbarExtension

def debug_tools_bar(app):
    """
    Set debuger tool bar
    """
    # the toolbar is only enabled in debug mode:
    app.debug = True
    # set a 'SECRET_KEY' to enable the Flask session cookies
    app.config['SECRET_KEY'] = app.config["DEV_DEBUG_TOOL_SECRET_KEY"] or 'jfhdfjshkjskjdjdhhe'
    toolbar = DebugToolbarExtension(app)
    return toolbar