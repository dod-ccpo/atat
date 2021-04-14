import datetime
import os
import time
import pytest
import random
import string

from selenium.common.exceptions import TimeoutException
from uitests.framework.page_objects.task_order_page import TaskOrderPage, time_run
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages

current_dir_path = "./uitests/framework/resources/test.pdf"
tnumber = datetime.datetime.now().strftime("%m%d%Y%H%M%S%f")[:-3]


@pytest.mark.smoke
class TestCreateTaskOrder:
    url2 = ReadConfig.getLoginLocalURL()

    def test_create_task_order(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "4. Create Active Task Order"}}'
        )
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
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        self.to = TaskOrderPage(self.driver)
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
        file_input.send_keys(absolute_file_path)
        self.to.click_next_add_TO_number()
        time.sleep(10)
        self.to.enter_TO_number(tnumber)
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
        time.sleep(5)
        self.to.click_confirm()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(10)
        self.to.click_checkbox_one()
        self.to.click_check_box_two()
        self.to.click_submit_TO()
        try:
            self.to.success_msg()
            activeto=str(time_run)
            self.to.active_to(activeto)
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to TaskOrder not matching"}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Text value matched"}}'
            )
        print(self.driver.title)
        self.driver.quit()


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))