import pytest

from atat.filters import dollars, renderAuditEvent, usPhone
from atat.models import AuditEvent


@pytest.mark.parametrize(
    "input,expected",
    [
        ("0", "$0.00"),
        ("123.00", "$123.00"),
        ("1234567", "$1,234,567.00"),
        ("-1234", "$-1,234.00"),
        ("one", "$0.00"),
    ],
)
def test_dollar_fomatter(input, expected):
    assert dollars(input) == expected


@pytest.mark.audit_log
def test_render_audit_event_with_known_resource_type():
    event = AuditEvent(resource_type="user")
    result = renderAuditEvent(event)
    assert "<article" in result


@pytest.mark.audit_log
def test_render_audit_event_with_unknown_resource_type():
    event = AuditEvent(resource_type="boat")
    result = renderAuditEvent(event)
    assert "<article" in result


def test_usPhone():
    assert usPhone("1234567890") == "+1 (123) 456 - 7890"
    assert usPhone(number=None) == ""
    assert usPhone(number="") == ""
