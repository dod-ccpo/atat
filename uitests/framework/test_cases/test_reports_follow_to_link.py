import os
import time
import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.page_objects.reports_page import ReportsPages
from uitests.framework.page_objects.task_order_page import (
    TaskOrderPage,
    random_no_generator,
)
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects import PageObjectMethods

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.daily
@pytest.mark.regression
class TestReportsFollowLink:
    url2 = ReadConfig.getLoginLocalURL()

    def test_reports_to_links(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "19. Reports-Follow-TO link"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # Initializing Common Methods
        self.cm = PageObjectMethods(self.driver)
        self.cm.validate_atat()
        # Initializing Portfolio page
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
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        # Initializing TaskOrder page
        self.to = TaskOrderPage(self.driver)
        self.to.click_task_order()
        self.to.validate_add_to()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_add_new_to()
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
        self.tnumber = random_no_generator()
        self.to.enter_TO_number(self.tnumber)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_next_add_clin_number()
        self.to.enter_clin_number("0001")
        self.to.add_clin_value("800000")
        self.to.add_obligated_clin_value("100000")
        self.to.add_start_month("01")
        self.to.add_start_day("01")
        self.to.add_start_year("2020")
        self.to.add_end_month("12")
        self.to.add_end_day("12")
        self.to.add_end_year("2021")
        self.to.click_next_review_TO()
        self.to.click_confirm()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_checkbox_one()
        self.to.click_check_box_two()
        self.to.click_submit_TO()
        self.to.success_msg()
        activeto = self.tnumber
        self.to.active_to(activeto)
        # Initializing Reports page
        self.rep = ReportsPages(self.driver)
        self.rep.click_reports()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        tpv = "$100,000.00"
        self.rep.total_portfolio_value(tpv)
        ofunds = "$100,000.00"
        self.rep.ob_funds(ofunds)
        self.rep.invoiced_exp_funds()
        self.rep.estimated_funds()
        rfunds = "$99,998.00"
        self.rep.remaining_funds(rfunds)
        self.rep.active_to_text()
        tno = self.tnumber
        self.rep.active_task_order_number(tno)
        print(tno)
        # click on the Active TO link
        self.rep.active_to_link()
        taskorderno = self.tnumber
        self.rep.valid_to_no_display(taskorderno)
        try:
            # verfying the total value
            totalvalue = "$800,000.00"
            self.rep.total_value(totalvalue)
            # verfying the total Obligated value
            totalob = "$100,000.00"
            self.rep.total_ob(totalob)
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to Total Value of the Active TaskOrder & Total Obligated amount not matching in the follow TO link view"}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Total Value of the Active TaskOrder & Total Obligated amount are matched in the follow TO link view"}}'
            )
        self.driver.quit()
