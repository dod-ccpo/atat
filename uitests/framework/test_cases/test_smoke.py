import os
import random
import string
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects.common_methods import JediCommonMethods
from uitests.framework.page_objects.application_page import CreateApplicationPages
from uitests.framework.page_objects.login_page import Login
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages
from uitests.framework.page_objects.reports_page import ReportsPages
from uitests.framework.page_objects.settings_page import SettingsPages
from uitests.framework.page_objects.task_orderpage import TaskOrderPage, time_run
from uitests.framework.test_cases.test_create_to import current_dir_path
from uitests.framework.utilities.read_properties import ReadConfig

current_dir_path = "C://Users//test.pdf"


class Test_Smoke:
    url2 = ReadConfig.getLoginLocalURL()

    def test_user_login(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "1. Verification of User Login"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        assert "ATAT" in self.driver.page_source
        self.login = Login(self.driver)
        self.login.userName()
        self.cm = JediCommonMethods(self.driver)
        self.cm.click_Home()
        self.login.clickLogout()
        assert "Access the JEDI Cloud" in self.driver.page_source
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "h3.usa-alert-heading"), "Logged out"
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Logout Not Successful"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Successfully Logged Out"}}'
            )
        print(self.driver.title)
        self.driver.quit()

    def test_create_application(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "5. Create Application"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "a.topbar__link span.topbar__link-label"), "ATAT"
            )
        )
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "header > nav > div > a:nth-child(1)"),
                "Brandon Buchannan",
            )
        )
        self.driver.execute_script(
            "document.querySelector('a.usa-button.usa-button-primary').scrollIntoView()"
        )
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.home__content"), "JEDI Cloud Services"
            )
        )
        self.app = CreateApplicationPages(self.driver)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.select_portfolio()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.usa-button.usa-button-primary")
            )
        ).click()
        time.sleep(10)
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-text"),
                "Name and Describe New Application",
            )
        )
        self.app.enter_app_name()
        self.app.enter_app_description()
        self.app.click_next_add_environments()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "Application Saved"
            )
        )
        self.app.click_next_add_members()
        time.sleep(10)
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.sticky-cta-text"), "Add Members"
            )
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_add_member()
        self.app.enter_first_name()
        self.app.enter_last_name()
        self.app.enter_email()
        self.app.enter_dod_id()
        self.app.click_next_roles()
        self.app.click_edit_item_box()
        self.app.click_manage_env_box()
        self.driver.execute_script(
            "document.querySelector('#environment_roles-0-role-None').value='ADMIN'"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_save_app()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "invitation has been sent"
            )
        )
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "#application-members"), "Application Team"
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Title matched!"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Title not matched"}}'
            )
        print(self.driver.title)
        self.driver.quit()

    def test_settings(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "2. Validating Settings Page"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(20)
        assert "ATAT" in self.driver.page_source
        self.set = SettingsPages(self.driver)
        self.set.select_portfolio()
        time.sleep(20)
        self.set.click_settings()
        time.sleep(20)
        assert "Portfolio name and component" in self.driver.page_source
        try:
            WebDriverWait(self.driver, 5).until(EC.title_contains("JEDI Cloud"))
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Title matched!"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Title not matched"}}'
            )
        print(self.driver.title)
        self.driver.quit()

    def test_reports_basic(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "6. Validating Reports - Basic"}}'
        )
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
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # self.rep.click_add_new_to()
        # time.sleep(20)
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

    def test_create_portfolio(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "3. Create Portfolio"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        assert "ATAT" in self.driver.page_source
        self.port = AddNewPortfolioPages(self.driver)
        self.port.click_new_portfolio()
        time.sleep(20)
        assert "Name and Describe Portfolio" in self.driver.page_source
        assert "New Portfolio" in self.driver.page_source
        self.pName = "Test Portfolio" + random_generator()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        # assert ("Add approved task orders" in self.driver.page_source)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "h3"), "Task Orders")
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Text is Matched"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Text is NOT Matched"}}'
            )
        print("Task Orders")
        self.driver.quit()

    def test_create_task_order(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "4. Create Active Task Order"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to = TaskOrderPage(self.driver)
        assert "New Portfolio" in self.driver.page_source
        self.to.select_portfolio()
        time.sleep(20)
        self.to.click_task_order()
        time.sleep(20)
        self.to.click_add_new_to()
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
        self.to.click_next_add_TO_number()
        time.sleep(20)
        self.to.enter_TO_number()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_next_add_clin_number()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(20)
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
        time.sleep(20)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.to.click_confirm()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(20)
        self.to.click_checkbox_one()
        self.to.click_check_box_two()
        self.to.click_submit_TO()
        time.sleep(20)
        assert (
            "Your Task Order has been uploaded successfully." in self.driver.page_source
        )
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "h3.usa-alert-heading"),
                    "Your Task Order has been uploaded successfully.",
                )
            )
            tmp = "Task Order #" + str(time_run)
            print(tmp)
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#Active h4"), tmp)
            )
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
