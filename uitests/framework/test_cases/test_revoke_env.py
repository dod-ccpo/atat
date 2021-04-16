import random
import string

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from uitests.framework.page_objects.application_page import CreateApplicationPages
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages
from uitests.framework.utilities.read_properties import ReadConfig


@pytest.mark.regression
class Test_010_revoke_environment:
    url2 = ReadConfig.getLoginLocalURL()

    def test_revoke_environment(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "13. Revoke Environment Access"}}'
        )

        # Initializing Page Objects
        self.cm = PageObjectMethods(self.driver)
        self.port = AddNewPortfolioPages(self.driver)
        self.app = CreateApplicationPages(self.driver)

        # Generator to create unique Portfolio name
        self.pName = "Test Portfolio" + random_generator()

        # Generator to create unique Application name
        self.appName = "App Name" + random_no_generator()

        # Generator to create unique email address
        self.email = random_generator() + "@gmail.com"

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.port.click_new_portfolio()
        self.port.validate_name_desc()
        self.port.validate_new_portfolio()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.cm.click_application()
        self.app.click_create_app()
        self.app.validate_name_desc()
        self.app.enter_app_name(self.appName)
        self.app.enter_app_description("App description goes here")
        self.app.click_next_add_environments()
        self.app.validate_app_save()
        self.app.click_next_add_members()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_add_team_member()
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
        self.app.click_save_app()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "invitation has been sent"
            )
        )
        self.app.click_save_app_next()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "li:nth-child(1) > div.accordion-table__item-content > div > div:nth-child(1) > span.label.label--default",
                ),
                "PENDING CREATION",
            )
        )
        self.app.click_toggle_menu()
        self.app.click_edit_roles_perm()
        assert "Manage Brandon Buchannan's Access" in self.driver.page_source
        self.app.click_revoke_env()
        self.app.validate_revoke_warning()
        self.app.click_save_revoke_env()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > h3"),
                    "Team member updated",
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Environment has been revoked"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Environment has NOT been revoked"}}'
            )
        print("Test: Revoke Environment")
        self.driver.quit()


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))


def random_no_generator(size=17, chars=string.digits):
    return "".join(random.choice(chars) for x in range(size))
