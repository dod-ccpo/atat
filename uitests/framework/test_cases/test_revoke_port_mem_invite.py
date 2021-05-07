import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects.application_page import CreateApplicationPages
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.settings_page import SettingsPages
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)


@pytest.mark.regression
class TestRevokePortfolioMemberInvite:
    url2 = ReadConfig.getLoginLocalURL()

    def test_revoke_port_mem_invite(self, setup):
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "15. Revoke Portfolio Member Invite"}}'
        )
        self.cm = PageObjectMethods(self.driver)
        self.port = AddNewPortfolioPages(self.driver)
        self.app = CreateApplicationPages(self.driver)
        self.set = SettingsPages(self.driver)
        self.pName = "Test Portfolio" + random_generator()
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
        self.set.click_settings()
        self.port.validating_name_comp()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.click_add_portfolio_manager()
        self.app.enter_first_name("Brandon")
        self.app.enter_last_name("Buchannan")
        self.email = random_generator() + "@gmail.com"
        self.app.enter_email(self.email)
        self.app.enter_dod_id("1230456789")
        self.app.click_next_roles()
        self.port.click_box_permissions_one()
        self.port.click_box_permissions_two()
        self.port.click_box_permissions_three()
        self.port.click_next_add_mem()
        self.port.validating_invite_sent()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_toggle_menu_b()
        self.port.click_revoke_invite()
        self.port.click_revoke_invite_confirm()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > h3"),
                    "Portfolio invitation revoked",
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
        print("Test: Revoke Portfolio Member Invite")
        self.driver.quit()
