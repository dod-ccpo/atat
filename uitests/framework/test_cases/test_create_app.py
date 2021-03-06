import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.application_page import CreateApplicationPages
from uitests.framework.page_objects.task_order_page import random_no_generator
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.utilities.browserstack import (
    set_session_name,
    set_session_status,
)


@pytest.mark.smoke
class TestCreateApplication:
    url2 = ReadConfig.getLoginLocalURL()

    def test_create_application(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script(set_session_name("5. Create Application"))

        # Initializing Page Objects
        self.app = CreateApplicationPages(self.driver)
        self.cm = PageObjectMethods(self.driver)
        self.port = AddNewPortfolioPages(self.driver)

        # Generator to create unique Application name
        self.appName = "App Name" + random_no_generator()

        # Generator to create unique email address
        self.email = random_generator() + "@gmail.com"

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.app.validate_name_brandon()
        self.driver.execute_script(
            "document.querySelector('a.usa-button.usa-button-primary').scrollIntoView()"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.select_portfolio()
        self.app.click_create_application()
        self.app.validate_name_desc()
        self.app.enter_app_name(self.appName)
        self.app.enter_app_description("App description goes here")
        self.app.click_next_add_environments()
        self.app.validate_app_save()
        self.app.click_next_add_members()
        self.app.validate_add_members()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
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
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_save_app()
        self.app.validate_invite_sent()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "#application-members"), "Application Team"
                )
            )
            self.driver.execute_script(set_session_status("passed", "Title matched!"))
        except TimeoutException:
            self.driver.execute_script(
                set_session_status("failed", "Title not matched")
            )
        print("Test: Create Application")
