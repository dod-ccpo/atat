from werkzeug.datastructures import FileStorage
import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, PropertyMock
import pendulum

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


def test_period_of_performance_is_first_to_last_clin():
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


def test_task_order_completed():
    assert TaskOrderFactory.create(clins=[CLINFactory.create()]).is_completed
    assert not TaskOrderFactory.create().is_completed
    assert not TaskOrderFactory.create(clins=[]).is_completed
    assert not TaskOrderFactory.create(number=None).is_completed


class TestTaskOrderStatus:
    @patch("atst.models.TaskOrder.is_completed", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_signed", new_callable=PropertyMock)
    def test_draft_status(self, is_signed, is_completed):
        # Given that I have a TO that is neither completed nor signed
        to = TaskOrder()
        is_signed.return_value = False
        is_completed.return_value = False

        assert to.status == Status.DRAFT

    @patch("atst.models.TaskOrder.end_date", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.start_date", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_completed", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_signed", new_callable=PropertyMock)
    def test_active_status(self, is_signed, is_completed, start_date, end_date):
        # Given that I have a signed TO and today is within its start_date and end_date
        today = pendulum.today().date()
        to = TaskOrder()

        start_date.return_value = today.subtract(days=1)
        end_date.return_value = today.add(days=1)
        is_signed.return_value = True
        is_completed.return_value = True

        # Its status should be active
        assert to.status == Status.ACTIVE

    @patch("atst.models.TaskOrder.end_date", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.start_date", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_completed", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_signed", new_callable=PropertyMock)
    def test_upcoming_status(self, is_signed, is_completed, start_date, end_date):
        # Given that I have a signed TO and today is before its start_date
        to = TaskOrder()
        start_date.return_value = pendulum.today().add(days=1).date()
        end_date.return_value = pendulum.today().add(days=2).date()
        is_signed.return_value = True
        is_completed.return_value = True

        # Its status should be upcoming
        assert to.status == Status.UPCOMING

    @patch("atst.models.TaskOrder.start_date", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.end_date", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_completed", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_signed", new_callable=PropertyMock)
    def test_expired_status(self, is_signed, is_completed, end_date, start_date):
        # Given that I have a signed TO and today is after its expiration date
        to = TaskOrder()
        end_date.return_value = pendulum.today().subtract(days=1).date()
        start_date.return_value = pendulum.today().subtract(days=2).date()
        is_signed.return_value = True
        is_completed.return_value = True

        # Its status should be expired
        assert to.status == Status.EXPIRED

    @patch("atst.models.TaskOrder.is_completed", new_callable=PropertyMock)
    @patch("atst.models.TaskOrder.is_signed", new_callable=PropertyMock)
    def test_unsigned_status(self, is_signed, is_completed):
        # Given that I have a TO that is completed but not signed
        to = TaskOrder(signed_at=pendulum.now().subtract(days=1))
        is_completed.return_value = True
        is_signed.return_value = False

        # Its status should be unsigned
        assert to.status == Status.UNSIGNED


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
