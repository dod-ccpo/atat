import re
from atat.utils.localization import translate
from flask import render_template
from jinja2 import contextfilter
from jinja2.exceptions import TemplateNotFound
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from decimal import DivisionByZero as DivisionByZeroException, InvalidOperation


def iconSvg(name):
    with open("static/icons/" + name + ".svg") as contents:
        return contents.read()


def dollars(value):
    try:
        numberValue = float(value)
    except ValueError:
        numberValue = 0
    return "${:,.2f}".format(numberValue)


def with_extra_params(url, **params):
    """
    Takes an existing url and safely appends additional query parms.
    """
    parsed_url = urlparse(url)
    parsed_params = parse_qs(parsed_url.query)
    new_params = {**parsed_params, **params}
    parsed_url = parsed_url._replace(query=urlencode(new_params))
    return urlunparse(parsed_url)


def usPhone(number):
    if not number:
        return ""
    phone = re.sub(r"\D", "", number)
    return "+1 ({}) {} - {}".format(phone[0:3], phone[3:6], phone[6:])


def obligatedFundingGraphWidth(values):
    numerator, denominator = values
    try:
        return (numerator / denominator) * 100
    except (DivisionByZeroException, InvalidOperation):
        return 0


def formattedDate(value, formatter="%m/%d/%Y"):
    if value:
        return value.strftime(formatter)
    else:
        return "-"


def pageWindow(pagination, size=2):
    page = pagination.page
    num_pages = pagination.pages

    over = max(0, page + size - num_pages)
    under = min(0, page - size - 1)

    return (max(1, (page - size) - over), min(num_pages, (page + size) - under))


def renderAuditEvent(event):
    template_name = "audit_log/events/{}.html".format(event.resource_type)
    try:
        return render_template(template_name, event=event)
    except TemplateNotFound:
        return render_template("audit_log/events/default.html", event=event)


def register_filters(app):
    app.jinja_env.filters["iconSvg"] = iconSvg
    app.jinja_env.filters["dollars"] = dollars
    app.jinja_env.filters["usPhone"] = usPhone
    app.jinja_env.filters["formattedDate"] = formattedDate
    app.jinja_env.filters["pageWindow"] = pageWindow
    app.jinja_env.filters["renderAuditEvent"] = renderAuditEvent
    app.jinja_env.filters["withExtraParams"] = with_extra_params
    app.jinja_env.filters["obligatedFundingGraphWidth"] = obligatedFundingGraphWidth

    @contextfilter
    def translateWithoutCache(context, *kwargs):
        return translate(*kwargs)

    if app.config["DEBUG"]:
        app.jinja_env.filters["translate"] = translateWithoutCache
    else:
        app.jinja_env.filters["translate"] = translate
