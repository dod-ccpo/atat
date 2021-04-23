import os
import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.page_objects.task_order_page import (
    TaskOrderPage,
    random_no_generator,
)
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects import PageObjectMethods

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.daily
@pytest.mark.regression
class TestTOIndexExpiredTO:
    url2 = ReadConfig.getLoginLocalURL()

    def test_to_index_expired_to(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": " 22.TO Index with Expired TO"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.cm = PageObjectMethods(self.driver)
        self.cm.validate_atat()
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
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.enter_clin_number("0112")
        self.to.add_clin_value("900,000")
        self.to.add_obligated_clin_value("200,000")
        self.to.add_start_month("11")
        self.to.add_start_day("01")
        self.to.add_start_year("2020")
        self.to.add_end_month("03")
        self.to.add_end_day("11")
        self.to.add_end_year("2021")
        self.to.click_next_review_TO()
        self.to.click_confirm()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_checkbox_one()
        self.to.click_check_box_two()
        self.to.click_submit_TO()
        # verifying the successful upload message
        self.to.success_msg()
        # Verifying the TO# under Expired TaskOrder section
        tmp = "Task Order #" + self.tnumber
        self.to.expired_to(tmp)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.collapse_all()
        self.to.click_active_to()
        self.to.active_blank_msg()
        self.to.click_draft_to()
        self.to.draft_blank_msg()
        self.to.click_future_to()
        self.to.upcoming_blank_msg()
        self.to.click_expired_to()
        try:
            tmp = "Task Order #" + self.tnumber
            self.to.expired_to(tmp)
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to TaskOrder not showing under Expired TaskOrder section"}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Expired TaskOrder value is showing under Expired Section and the TaskOrder number is matched"}}'
            )
        self.driver.quit()
