import os
import time
import pytest


from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.task_order_page import TaskOrderPage
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects import PageObjectMethods

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.regression
class TestCreateDraftTaskOrder:
    url2 = ReadConfig.getLoginLocalURL()

    def test_create_draft_task_order(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "9. Create Draft TO"}}'
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
        # Random Generator for unique Portfolio Name
        self.pName = "Test Portfolio" + random_generator()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        time.sleep(5)
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        self.to = TaskOrderPage(self.driver)
        self.to.click_task_order()
        self.to.validate_add_to()
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
        self.to.cancel_btn_on_add_to()
        self.to.save_later_yes_btn()
        # verifying the Draft section and the Task Order displays as New TaskOrder
        temp = "New Task Order"
        self.to.draft_to(temp)
        try:
            draftTotalValue = "$0.00"
            self.to.draft_total_value(draftTotalValue)
            draftTotalObligated = "$0.00"
            self.to.draft_total_obligated(draftTotalObligated)
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to TotalValue & Total Obligated for the Draft TaskOrder values are not matching"}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"TotalValue for the Draft Task Order& Total Obligated for the Draft TaskOrder values are matching"}}'
            )
        self.driver.quit()
