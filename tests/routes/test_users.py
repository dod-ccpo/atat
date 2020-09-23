from flask import url_for

from atat.domain.users import Users
from tests.factories import UserFactory


def test_user_can_view_profile(user_session, client):
    user = UserFactory.create()
    user_session(user)
    response = client.get(url_for("users.user"))
    assert user.email in response.data.decode()


def test_user_can_update_profile(user_session, client):
    user = UserFactory.create()
    user_session(user)
    new_data = {**user.to_dictionary(), "first_name": "chad", "last_name": "vader"}
    client.post(url_for("users.update_user"), data=new_data)
    updated_user = Users.get_by_dod_id(user.dod_id)
    assert updated_user.first_name == "chad"
    assert updated_user.last_name == "vader"


def test_user_is_redirected_when_updating_profile(user_session, client):
    user = UserFactory.create()
    user_session(user)
    next_url = "/home"

    user_data = user.to_dictionary()
    response = client.post(
        url_for("users.update_user", next=next_url),
        data=user_data,
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.location.endswith(next_url)
