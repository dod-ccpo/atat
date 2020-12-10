from flask import current_app as app
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.routing import RequestRedirect


def match_url_pattern(url, method="GET"):
    """Ensure a url matches a url pattern in the flask app
    inspired by https://stackoverflow.com/questions/38488134/get-the-flask-view-function-that-matches-a-url/38488506#38488506
    """
    server_name = app.config.get("SERVER_NAME") or "localhost"
    adapter = app.url_map.bind(server_name=server_name)

    try:
        match = adapter.match(url, method=method)
    except RequestRedirect as e:
        # recursively match redirects
        return match_url_pattern(e.new_url, method)
    except (MethodNotAllowed, NotFound):
        # no match
        app.logger.warning(f"URL didn't match pattern: {method} {url}")
        return None

    if match[0] in app.view_functions:
        return url
