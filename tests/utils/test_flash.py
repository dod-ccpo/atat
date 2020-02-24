from atat.utils.flash import formatted_flash as flash
from flask import get_flashed_messages


def test_flash_message():
    flash("revoked_portfolio_access", member_name="Lando")
    messages = get_flashed_messages()
    message_info = messages[0]
    assert "message" in message_info
    assert "Lando" in message_info["message"]
