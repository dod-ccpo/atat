from werkzeug.datastructures import FileStorage
import pytest
from datetime import date

from atst.models import *
from atst.models.clin import JEDICLINType
from atst.models.task_order import TaskOrder, Status

from tests.factories import (
    CLINFactory,
    random_future_date,
    random_past_date,
    TaskOrderFactory,
)
from tests.mocks import PDF_FILENAME


class TestPeriodOfPerformance:
    def test_period_of_performance_is_first_to_last_clin(self):
        start_date = date(2019, 6, 6)
        end_date = date(2020, 6, 6)

        intermediate_start_date = date(2019, 7, 1)
        intermediate_end_date = date(2020, 3, 1)

        task_order = TaskOrderFactory.create(
            clins=[
                CLINFactory.create(
                    start_date=intermediate_start_date, end_date=intermediate_end_date
                ),
                CLINFactory.create(
                    start_date=start_date, end_date=intermediate_end_date
                ),
                CLINFactory.create(
                    start_date=intermediate_start_date, end_date=intermediate_end_date
                ),
                CLINFactory.create(
                    start_date=intermediate_start_date, end_date=end_date
                ),
                CLINFactory.create(
                    start_date=intermediate_start_date, end_date=intermediate_end_date
                ),
            ]
        )

        assert task_order.start_date == start_date
        assert task_order.end_date == end_date


class TestTaskOrderStatus:
    @pytest.mark.skip(reason="Reimplement after adding CLINs")
    def test_started_status(self):
        to = TaskOrder()
        assert to.status == Status.STARTED

    @pytest.mark.skip(reason="See if still needed after implementing CLINs")
    def test_pending_status(self):
        to = TaskOrder(number="42")
        assert to.status == Status.PENDING

    @pytest.mark.skip(reason="See if still needed after implementing CLINs")
    def test_active_status(self):
        to = TaskOrder(number="42")
        assert to.status == Status.ACTIVE

    @pytest.mark.skip(reason="See if still needed after implementing CLINs")
    def test_expired_status(self):
        to = TaskOrder(number="42")
        assert to.status == Status.EXPIRED


class TestBudget:
    def test_total_contract_amount(self):
        to = TaskOrder()
        assert to.total_contract_amount == 0

        clin1 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_1)
        clin2 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_2)
        clin3 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_3)

        assert (
            to.total_contract_amount
            == clin1.obligated_amount + clin2.obligated_amount + clin3.obligated_amount
        )

    def test_total_obligated_funds(self):
        to = TaskOrder()
        clin4 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_4)
        assert to.total_obligated_funds == 0

        clin1 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_1)
        clin2 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_2)
        clin3 = CLINFactory(task_order=to, jedi_clin_type=JEDICLINType.JEDI_CLIN_3)
        assert (
            to.total_obligated_funds == clin1.obligated_amount + clin3.obligated_amount
        )


class TestPDF:
    def test_setting_pdf_with_attachment(self):
        to = TaskOrder()
        attachment = Attachment(filename="sample.pdf", object_name="sample")
        to.pdf = attachment

        assert to.pdf_attachment_id == attachment.id

    def test_setting_pdf_with_file_storage(self):
        to = TaskOrder()
        with open(PDF_FILENAME, "rb") as fp:
            fs = FileStorage(fp, content_type="application/pdf")
            to.pdf = fs

        assert to.pdf is not None
        assert to.pdf.filename == PDF_FILENAME

    def test_setting_pdf_with_invalid_object(self):
        to = TaskOrder()
        with pytest.raises(TypeError):
            to.pdf = "invalid"

    def test_setting_pdf_with_empty_value(self):
        to = TaskOrder()
        assert to.pdf is None

        to.pdf = ""
        assert to.pdf is None

    def test_removing_pdf(self):
        attachment = Attachment(filename="sample.pdf", object_name="sample")
        to = TaskOrder(pdf=attachment)
        assert to.pdf is not None

        to.pdf = ""
        assert to.pdf is None
