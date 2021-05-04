import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages, random_generator
from uitests.framework.page_objects.task_order_page import random_no_generator
from uitests.framework.page_objects.application_page import CreateApplicationPages
from uitests.framework.page_objects import PageObjectMethods


@pytest.mark.AT6163
@pytest.mark.regression
class TestApplicationWithIndex:
    url2 = ReadConfig.getLoginLocalURL()

    def test_app_index_app(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "33. Application Index"}}'
        )

        # Initializing Page Objects
        self.app = CreateApplicationPages(self.driver)
        self.cm = PageObjectMethods(self.driver)
        self.port = AddNewPortfolioPages(self.driver)

        # Generator to create unique Portfolio name
        self.pName = "Test Portfolio" + random_generator()

        # Generator to create unique Application name
        self.appName = "App Name" + random_no_generator()

        # Generator to create unique email address
        self.email = random_generator() + "@gmail.com"

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.port.click_new_portfolio()
        self.port.validate_new_portfolio()
        self.port.validate_name_desc()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.app.click_applications()
        self.app.click_create_application()
        self.app.validate_name_desc()
        self.app.enter_app_name(self.appName)
        self.app.enter_app_description("App description goes here")
        self.app.click_next_add_environments()
        self.app.validate_app_save()
        self.app.click_next_add_members()
        self.app.validate_add_members()
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_add_member()
        self.app.enter_first_name("Brandon")
        self.app.enter_last_name("Buchannan")
        self.app.enter_email(self.email)
        self.app.enter_dod_id("1230456789")
        self.app.click_next_roles()
        self.app.click_edit_item_box()
        self.app.click_manage_env_box()
        self.driver.execute_script(
            "document.querySelector('#environment_roles-0-role-None').value='ADMIN'"
        )
        self.driver.execute_script(
            "document.querySelector('#environment_roles-1-role-None').value='BILLING_READ'"
        )
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_save_app()
        self.app.click_save_app_next()
        self.app.click_applications()
        self.app.click_acc()
        self.app.validate_acc_dev()
        self.app.validate_acc_prod()
        self.app.validate_acc_stage()
        self.app.validate_acc_test()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (
                        By.CSS_SELECTOR,
                        "div.portfolio-applications > div > div.action-group > a",
                    ),
                    "Collapse All",
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Application Indexing Verified"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Indexing Not Verified"}}'
            )
        print("Test: Verification of Application Indexing")
        self.driver.quit()
