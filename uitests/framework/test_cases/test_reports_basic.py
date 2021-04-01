import datetime
import os
import random
import string
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from uitests.framework.page_objects.reports_page import ReportsPages, time_run
from uitests.framework.utilities.read_properties import ReadConfig

current_dir_path = "C://Users//test.pdf"


class Test_002_Create_Task_order:
    url2 = ReadConfig.getLoginLocalURL()

    def test_reports_basic(self, setup):
        self.driver = setup
        # self.driver.execute_script('browserstack_executor: {"action": "setSessionName", '
        #                            '"arguments": {"name": "7. Reports - Basic"}}')
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        assert "ATAT" in self.driver.page_source
        self.rep = ReportsPages(self.driver)
        assert "New Portfolio" in self.driver.page_source
        self.rep.click_new_portfolio()
        time.sleep(20)
        assert "Name and Describe Portfolio" in self.driver.page_source
        assert "New Portfolio" in self.driver.page_source
        self.pName = "Test Portfolio" + random_generator()
        self.rep.enter_portfolio_name(self.pName)
        self.rep.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.rep.select_checkbox()
        self.rep.click_save_portfolio_btn()
        time.sleep(20)
        self.rep.click_task_order()
        time.sleep(20)
        assert "Add Task Order" in self.driver.page_source
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.rep.click_add_new_to()
        time.sleep(20)
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
        self.rep.click_next_add_TO_number()
        time.sleep(20)
        self.rep.enter_TO_number()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.rep.click_next_add_clin_number()
        self.rep.enter_clin_number("0001")
        self.rep.add_clin_value("800000")
        self.rep.add_obligated_clin_value("100000")
        self.rep.add_start_month("01")
        self.rep.add_start_day("01")
        self.rep.add_start_year("2020")
        self.rep.add_end_month("12")
        self.rep.add_end_day("12")
        self.rep.add_end_year("2021")
        self.rep.click_next_review_TO()
        time.sleep(5)
        self.rep.click_confirm()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(20)
        self.rep.click_checkbox_one()
        self.rep.click_check_box_two()
        self.rep.click_submit_TO()
        time.sleep(20)
        assert (
            "Your Task Order has been uploaded successfully." in self.driver.page_source
        )
        self.rep.click_reports()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.jedi-clin-funding__clin-wrapper > h3"),
                "$100,000.00",
            )
        )
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(1) > p.h3.jedi-clin-funding__meta-value",
                ),
                "$1.00",
            )
        )
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(2) > p.h3.jedi-clin-funding__meta-value",
                ),
                "$1.00",
            )
        )
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(3) > p.h3.jedi-clin-funding__meta-value",
                ),
                "$99,998.00",
            )
        )
        assert "Current Obligated funds" in self.driver.page_source
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.jedi-clin-funding__active-task-orders > h3"),
                    "Active Task Orders",
                )
            )
            tmp = "Task Order #" + str(time_run)
            print(tmp)
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#Active h4"), tmp)
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Text value matched"}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to TaskOrder not matching"}}'
            )
        print(self.driver.title)
        self.driver.quit()


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))
