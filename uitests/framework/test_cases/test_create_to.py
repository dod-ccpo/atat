import os
import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.task_order_page import (
    TaskOrderPage,
    random_no_generator,
)
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.utilities.browserstack import (
    set_session_name,
    set_session_status,
)

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.smoke
class TestCreateTaskOrder:
    url2 = ReadConfig.getLoginLocalURL()

    def test_create_task_order(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(set_session_name("4. Create Active Task Order"))

        # Initializing Page Objects
        self.port = AddNewPortfolioPages(self.driver)
        self.to = TaskOrderPage(self.driver)
        self.cm = PageObjectMethods(self.driver)

        # Generator to create unique Portfolio name
        self.pName = "Test Portfolio" + random_generator()

        # Generator to create unique Task Order number
        self.toNumber = random_no_generator()

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.port.click_new_portfolio()
        self.port.validate_new_portfolio()
        self.port.validate_name_desc()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        self.to.click_task_order()
        self.to.validate_add_to()
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
        assert (
            file_input.is_enabled() is True
        ), "File input element is expected to be enabled before PDF upload, but is not enabled."
        file_input.send_keys(absolute_file_path)
        file_input_disable = self.driver.find_element_by_css_selector(
            "#pdf"
        ).is_enabled()
        assert (
            file_input_disable is False
        ), "File input element is expected to be disabled after PDF upload, but is enabled."
        self.to.click_next_add_TO_number()
        self.to.enter_TO_number(self.toNumber)
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
        try:
            self.to.success_msg()
            activeto = self.toNumber
            self.to.active_to(activeto)
        except TimeoutException:
            self.driver.execute_script(
                set_session_status("failed", "Timed out due to TaskOrder not matching")
            )
        else:
            self.driver.execute_script(
                set_session_status("passed", "Text value matched")
            )
        print("Test: Create Active Task Order")
