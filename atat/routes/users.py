import pendulum
from flask import Blueprint, g, redirect, render_template
from flask import request as http_request

from atat.domain.users import Users
from atat.forms.edit_user import EditUserForm
from atat.routes import match_url_pattern
from atat.utils.flash import formatted_flash as flash

bp = Blueprint("users", __name__)


@bp.route("/user")
def user():
    user = g.current_user
    form = EditUserForm(data=user.to_dictionary())
    next_ = http_request.args.get("next")

    if next_:
        flash("user_must_complete_profile")

    return render_template(
        "user/edit.html",
        next=next_,
        form=form,
        user=user,
        mindate=pendulum.now(tz="UTC").subtract(days=365),
        maxdate=pendulum.now(tz="UTC"),
    )


@bp.route("/user", methods=["POST"])
def update_user():
    user = g.current_user
    form = EditUserForm(http_request.form)
    next_url = http_request.args.get("next")
    if form.validate():
        Users.update(user, form.data)
        flash("user_updated")
        if match_url_pattern(next_url):
            return redirect(next_url)

    return render_template(
        "user/edit.html",
        form=form,
        user=user,
        next=next_url,
        mindate=pendulum.now(tz="UTC").subtract(days=365),
        maxdate=pendulum.now(tz="UTC"),
    )
