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
class TestTOStep4AddClin:
    url2 = ReadConfig.getLoginLocalURL()

    def test_to_step4_add_clin(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": " 28.TO Step 4 - with-2 CLINs"}}'
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
        self.to.enter_clin_number("0033")
        clinNumber = "CLIN 0033"
        self.to.clin_card_title(clinNumber)
        self.to.add_clin_value("900,000")
        self.to.add_obligated_clin_value("200,000")
        percentObligated = "22%"
        self.to.percent_obligated(percentObligated)
        self.to.add_start_month("11")
        self.to.add_start_day("01")
        self.to.add_start_year("2020")
        self.to.add_end_month("09")
        self.to.add_end_day("12")
        self.to.add_end_year("2022")
        self.to.click_add_another_clin()
        self.to.enter_clin_number2("0034")
        self.to.select_idiq_number2()
        self.to.add_total_clin2_value("300,000")
        self.to.add_obligated_clin2_value("200,000")
        self.to.add_start_month_clin2("12")
        self.to.add_start_day_clin2("12")
        self.to.add_start_year_clin2("2020")
        self.to.add_end_month_clin2("12")
        self.to.add_end_day_clin2("12")
        self.to.add_end_year_clin2("2021")
        self.to.click_next_review_TO()
        self.to.validate_step4_header()
        toNumber = self.tnumber
        self.to.validate_to_no_step4(toNumber)
        step4_total_value = "$1,200,000.00"
        self.to.validate_step4_total_value(step4_total_value)
        step4_total_ob_value = "$400,000.00"
        self.to.validate_step4_total_ob_value(step4_total_ob_value)
        # Verifying the CLIN1 under CLIN Summary details
        clin1 = "0033"
        self.to.clin_one(clin1)
        dates = "11/01/2020 - 09/12/2022"
        self.to.clin_one_pop(dates)
        clinOneValue = "$900,000.00"
        self.to.clin_one_value(clinOneValue)
        clinOneAmountObligated = "$200,000.00"
        self.to.clin_one_amount_obligated(clinOneAmountObligated)
        # Verifying the CLIN2 under CLIN Summary details
        clin2 = "0034"
        self.to.clin_two(clin2)
        datesForClin2 = "12/12/2020 - 12/12/2021"
        self.to.clin_two_pop(datesForClin2)
        clinTwoValue = "$300,000.00"
        self.to.clin_two_value(clinTwoValue)
        clinTwoAmountObligated = "$200,000.00"
        self.to.clin_two_amount_obligated(clinTwoAmountObligated)
        try:
            self.to.click_confirm()
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Next:Confirm Button is enabled and able to click and CLIN Numbers are showing as expected"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to Next:Confirm Button is not enabled or clickable"}}'
            )
        self.driver.quit()
