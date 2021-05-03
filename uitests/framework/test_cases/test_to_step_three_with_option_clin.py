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
from uitests.framework.utilities.browserstack import (
    set_session_name,
    set_session_status,
)

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.daily
@pytest.mark.regression
class TestTOStep3OptionClin:
    url2 = ReadConfig.getLoginLocalURL()

    def test_to_step3_option_clin(self, setup):
        self.driver = setup
        self.driver.execute_script(set_session_name(" 26.TO Step 3 -with Option CLIN"))
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
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
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        # Initializing the TaskOrderPage
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
        self.to.enter_clin_number("0022")
        clinNumber = "CLIN 0022"
        self.to.clin_card_title(clinNumber)
        self.to.add_clin_value("900,000")
        self.to.add_obligated_clin_value("200,000")
        percentObligated = "22%"
        self.to.percent_obligated(percentObligated)
        self.to.add_start_month("1")
        self.to.add_start_day("01")
        self.to.add_start_year("2021")
        self.to.add_end_month("09")
        self.to.add_end_day("12")
        self.to.add_end_year("2022")
        self.to.validate_add_clin_btn()
        try:
            self.to.click_next_review_TO()
            self.driver.execute_script(
                set_session_name(
                    "passed",
                    "Next:Review TaskOrder Button is enabled and able to click",
                )
            )
        except TimeoutException:
            self.driver.execute_script(
                set_session_name(
                    "failed",
                    "Timed out due to Next:Review TaskOrder Button is not enabled or clickable",
                )
            )
