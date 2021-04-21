import os
import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages, random_generator
from uitests.framework.page_objects.task_order_page import TaskOrderPage, random_no_generator
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects import PageObjectMethods

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.daily
@pytest.mark.regression
class TestTOIndexwithUnconfirmedTO:
    url2 = ReadConfig.getLoginLocalURL()

    def test_to_index_unconfirmed_to(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": " 24.TO Index with Unconfirmed TO"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        # Initializing the CommonMethods
        self.cm = PageObjectMethods(self.driver)
        self.cm.validate_atat()
        # Initializing the PortfolioPageObjects
        self.port = AddNewPortfolioPages(self.driver)
        self.port.click_new_portfolio()
        self.port.validate_new_portfolio()
        self.port.validate_name_desc()
        self.pName = "Test Portfolio" + random_generator()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        # Initializing the TaskOrderPage
        self.to = TaskOrderPage(self.driver)
        self.to.click_task_order()
        self.to.validate_add_to()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_add_new_to()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
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
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_next_add_clin_number()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.to.enter_clin_number("0012")
        self.to.add_clin_value("900,000")
        self.to.add_obligated_clin_value("200,000")
        self.to.add_start_month("11")
        self.to.add_start_day("01")
        self.to.add_start_year("2020")
        self.to.add_end_month("09")
        self.to.add_end_day("12")
        self.to.add_end_year("2022")
        self.to.click_next_review_TO()
        self.to.click_confirm()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_checkbox_one()
        self.to.click_check_box_two()
        self.to.click_submit_TO()
        # Verifying the successful upload message
        self.to.success_msg()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        # Click on AddNewTaskOrder
        self.to.add_new_to_button()
        # Navigates to Upload TaskOrderPage
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
        self.t1number = random_no_generator()
        self.to.enter_TO_number(self.t1number)
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_next_add_clin_number()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.to.enter_clin_number("0013")
        self.to.add_clin_value("500,000")
        self.to.add_obligated_clin_value("200,000")
        self.to.add_start_month("11")
        self.to.add_start_day("01")
        self.to.add_start_year("2020")
        self.to.add_end_month("09")
        self.to.add_end_day("13")
        self.to.add_end_year("2022")
        self.to.click_next_review_TO()
        self.to.step4_cancel_button()
        self.to.yes_later_btn()
        # Verifying the TO# under Active TaskOrder section
        tmp = "Task Order #" + self.tnumber
        self.to.active_to(tmp)
        # Verifying the TO# under Draft TaskOrder section
        temp = self.t1number
        self.to.draft_to(temp)
        try:

            draftTotalValue = "$500,000.00"
            self.to.draft_total_value(draftTotalValue)
            draftTotalObligated = "$200,000.00"
            self.to.draft_total_obligated(draftTotalObligated)
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to Draft TaskOrder Total Value & Draft TaskOrder Total Obligated value not matching under Draft  TaskOrder section"}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '" Draft TaskOrder Total Value & Draft TaskOrder Total Obligated value  section are matched under Draft  TaskOrder"}}'
            )
        self.driver.quit()
