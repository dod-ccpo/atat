import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects.application_page import CreateApplicationPages
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.settings_page import SettingsPages
from uitests.framework.page_objects.task_order_page import (
    TaskOrderPage,
    random_no_generator,
)
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)


@pytest.mark.regression
class TestResendAppMemInvite:
    url2 = ReadConfig.getLoginLocalURL()

    def test_resend_app_mem_invite(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "17. Resend Application Member Invite"}}'
        )

        # Initializing Page Objects
        self.cm = PageObjectMethods(self.driver)
        self.port = AddNewPortfolioPages(self.driver)
        self.app = CreateApplicationPages(self.driver)
        self.set = SettingsPages(self.driver)
        self.to = TaskOrderPage(self.driver)

        # Generator to create random Test Portfolio name
        self.pName = "Test Portfolio" + random_generator()

        # Generator to create unique Application name
        self.appName = "App Name" + random_no_generator()

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.port.click_new_portfolio()
        self.port.validate_name_desc()
        self.port.validate_new_portfolio()

        # Entering portfolio name from generator
        self.port.enter_portfolio_name(self.pName)

        self.port.enter_portfolio_description(
            "Entering the description to verify the text"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.to.validate_add_to()
        self.app.click_applications()
        self.app.click_create_app()
        self.app.enter_app_name(self.appName)
        self.app.enter_app_description("App description goes here")
        self.app.click_next_add_environments()
        self.app.validate_app_save()
        self.app.click_next_add_members()
        self.app.click_add_member()
        self.app.enter_first_name("Brandon")
        self.app.enter_last_name("Buchannan")
        self.email = random_generator() + "@gmail.com"
        self.app.enter_email(self.email)
        self.app.enter_dod_id("1230456789")
        self.app.click_next_roles()
        self.port.click_box_permissions_one()
        self.port.click_box_permissions_two()
        self.port.click_next_add_mem()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_save_app_next()
        self.app.validate_env_access()
        self.driver.execute_script("window.scrollBy(0, 150);")
        self.app.click_toggle_menu()
        self.port.click_resend_invite_b()
        assert "Verify Member Information" in self.driver.page_source
        self.port.click_resend_invite_confirm_b()
        self.driver.execute_script("window.scrollTo(0, 0);")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > p"),
                    "has been sent an invitation to access this Application",
                )
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
        print("Test: Resend Application Member Invite")
        self.driver.quit()
