import pendulum
from dateutil.relativedelta import relativedelta
from flask import current_app as app

from atat.forms.task_order import CLINForm, TaskOrderForm
from atat.models import JEDICLINType
from atat.utils.localization import translate

import tests.factories as factories


def test_clin_form_jedi_clin_type():
    jedi_type = JEDICLINType.JEDI_CLIN_2
    clin = factories.CLINFactory.create(jedi_clin_type=jedi_type)
    clin_form = CLINForm(obj=clin)
    assert clin_form.jedi_clin_type.data == jedi_type.value


def test_clin_form_start_date_before_end_date():
    invalid_start = pendulum.date(2020, 12, 12)
    invalid_end = pendulum.date(2020, 1, 1)
    invalid_clin = factories.CLINFactory.create(
        start_date=invalid_start, end_date=invalid_end
    )
    clin_form = CLINForm(obj=invalid_clin)
    assert not clin_form.validate()
    assert (
        translate("forms.task_order.pop_errors.date_order")
        in clin_form.start_date.errors
    )
    valid_start = pendulum.date(2020, 1, 1)
    valid_end = pendulum.date(2020, 12, 12)
    valid_clin = factories.CLINFactory.create(
        start_date=valid_start, end_date=valid_end
    )
    valid_clin_form = CLINForm(obj=valid_clin)
    assert valid_clin_form.validate()


def test_clin_form_pop_dates_within_contract_dates():
    CONTRACT_START_DATE = app.config.get("CONTRACT_START_DATE")
    CONTRACT_END_DATE = app.config.get("CONTRACT_END_DATE")

    invalid_start = CONTRACT_START_DATE - relativedelta(months=1)
    invalid_end = CONTRACT_END_DATE + relativedelta(months=1)
    invalid_clin = factories.CLINFactory.create(
        start_date=invalid_start, end_date=invalid_end
    )
    clin_form = CLINForm(obj=invalid_clin)

    assert not clin_form.validate()
    assert (
        translate(
            "forms.task_order.pop_errors.range",
            {
                "start": CONTRACT_START_DATE.strftime("%b %d, %Y"),
                "end": CONTRACT_END_DATE.strftime("%b %d, %Y"),
            },
        )
    ) in clin_form.start_date.errors
    assert (
        translate(
            "forms.task_order.pop_errors.range",
            {
                "start": CONTRACT_START_DATE.strftime("%b %d, %Y"),
                "end": CONTRACT_END_DATE.strftime("%b %d, %Y"),
            },
        )
    ) in clin_form.end_date.errors

    valid_start = CONTRACT_START_DATE + relativedelta(months=1)
    valid_end = CONTRACT_END_DATE - relativedelta(months=1)
    valid_clin = factories.CLINFactory.create(
        start_date=valid_start, end_date=valid_end
    )
    valid_clin_form = CLINForm(obj=valid_clin)
    assert valid_clin_form.validate()


def test_clin_form_obligated_greater_than_total():
    invalid_clin = factories.CLINFactory.create(
        total_amount=0,
        obligated_amount=1,
        start_date=pendulum.date(2019, 9, 15),
        end_date=pendulum.date(2020, 9, 14),
    )
    invalid_clin_form = CLINForm(obj=invalid_clin)
    assert not invalid_clin_form.validate()
    assert (
        translate("forms.task_order.clin_funding_errors.obligated_amount_error")
    ) in invalid_clin_form.obligated_amount.errors


def test_clin_form_dollar_amounts_out_of_range():
    invalid_clin = factories.CLINFactory.create(
        total_amount=-1,
        obligated_amount=1000000001,
        start_date=pendulum.date(2019, 9, 15),
        end_date=pendulum.date(2020, 9, 14),
    )
    invalid_clin_form = CLINForm(obj=invalid_clin)
    assert not invalid_clin_form.validate()
    assert (
        translate("forms.task_order.clin_funding_errors.funding_range_error")
    ) in invalid_clin_form.total_amount.errors
    assert (
        translate("forms.task_order.clin_funding_errors.funding_range_error")
    ) in invalid_clin_form.obligated_amount.errors


def test_no_number():
    http_request_form_data = {}
    form = TaskOrderForm(http_request_form_data)
    assert form.data["number"] is None


def test_number_allows_alphanumeric():
    valid_to_numbers = ["1234567890123", "ABC1234567890"]

    for number in valid_to_numbers:
        form = TaskOrderForm({"number": number})
        assert form.validate()


def test_number_allows_between_13_and_17_characters():
    valid_to_numbers = ["123456789012345", "ABCDEFG1234567890"]

    for number in valid_to_numbers:
        form = TaskOrderForm({"number": number})
        assert form.validate()


def test_number_strips_dashes():
    valid_to_numbers = ["123-456789-012345", "ABCD-EFG12345-67890"]

    for number in valid_to_numbers:
        form = TaskOrderForm({"number": number})
        assert form.validate()
        assert not "-" in form.number.data


def test_number_case_coerces_all_caps():
    valid_to_numbers = ["12345678012345", "AbcEFg1234567890"]

    for number in valid_to_numbers:
        form = TaskOrderForm({"number": number})
        assert form.validate()
        assert form.number.data == number.upper()
