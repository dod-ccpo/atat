import os
import time
import random
import string
import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages
from uitests.framework.page_objects.task_order_page import TaskOrderPage
from uitests.framework.page_objects.reports_page import ReportsPages
from uitests.framework.utilities.read_properties import ReadConfig

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.regression
class TestExpiredToReports:
    url2 = ReadConfig.getLoginLocalURL()

    def test_expired_to_reports(self, setup):
        self.driver = setup
        self.driver.execute_script('browserstack_executor: {"action": "setSessionName", '
                                   '"arguments": {"name": "12.Reports-with expired TO"}}')
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        assert "ATAT" in self.driver.page_source
        self.port = AddNewPortfolioPages(self.driver)
        self.port.click_new_portfolio()
        self.port.validate_new_portfolio()
        self.port.validate_name_desc()
        self.pName = "Test Portfolio" + random_generator()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        time.sleep(5)
        self.port.click_save_portfolio_btn()
        # verifying the Portfolio name on Task Order page
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        self.to = TaskOrderPage(self.driver)
        self.to.click_task_order()
        self.to.validate_add_to()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_add_new_to()
        assert "Upload your approved Task Order" in self.driver.page_source
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            "document.querySelector('#pdf').style.visibility = 'visible'"
        )
        self.driver.execute_script(
            "document.querySelector('#pdf').style.display = 'block'"
        )
        absolute_file_path = os.path.abspath(current_dir_path)
        file_input = self.driver.find_element_by_id("pdf")
        file_input.send_keys(absolute_file_path)
        self.to.click_next_add_TO_number()
        time.sleep(10)
        self.tnumber = random_no_generator()
        self.to.enter_TO_number(self.tnumber)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_next_add_clin_number()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.enter_clin_number("0012")
        self.to.add_clin_value("800,000")
        self.to.add_obligated_clin_value("100,000")
        self.to.add_start_month("12")
        self.to.add_start_day("13")
        self.to.add_start_year("2020")
        self.to.add_end_month("03")
        self.to.add_end_day("31")
        self.to.add_end_year("2021")
        self.to.click_next_review_TO()
        self.to.click_confirm()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_checkbox_one()
        self.to.click_check_box_two()
        self.to.click_submit_TO()
        self.to.success_msg()
        tmp = 'Task Order #' + self.tnumber
        self.to.expired_to(tmp)
        # Navigate to the Reports page
        self.rep = ReportsPages(self.driver)
        self.rep.click_reports()
        self.rep.report_page_is_displayed()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.rep.msg_insuf_funds()
        # verify the Total Portfolio value
        tpv = "$0.00"
        self.rep.total_portfolio_value(tpv)
        # verify the Days Remaining
        days = "0 days"
        self.rep.days_remaining(days)
        # verifying the Obligated funds
        ofunds = "0.00"
        self.rep.ob_funds(ofunds)
        self.rep.invoiced_exp_funds()
        self.rep.estimated_funds()
        rfunds = "$-2.00"
        self.rep.remaining_funds(rfunds)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.rep.expired_funding_click()
        # verify the TO# number under expired funding
        extonumber = self.tnumber
        self.rep.expired_to_details(extonumber)
        print(extonumber)
        try:
            periodofperformance = "Dec 13, 2020 - Mar 31, 2021"
            self.rep.pop(periodofperformance)
            amountOb = "100,000"
            self.rep.amount_obligated((amountOb))
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to PoP & Amount Obligated are not matched under expired funding "}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"PoP & Amount Obligated are matched under expired funding"}}'
            )
        self.driver.quit()


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))


def random_no_generator(size=17, chars=string.digits):
    return ''.join(random.choice(chars) for x in range(size))
