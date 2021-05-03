import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.application_page import CreateApplicationPages
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from uitests.framework.utilities.browserstack import (
    set_session_name,
    set_session_status,
)

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.AT6163
@pytest.mark.regression
class TestEditPortMem:
    url2 = ReadConfig.getLoginLocalURL()

    def test_edit_port_mem(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(set_session_name("31. Edit Portfolio Member"))

        # Initializing Page Objects
        self.port = AddNewPortfolioPages(self.driver)
        self.cm = PageObjectMethods(self.driver)
        self.app = CreateApplicationPages(self.driver)

        # Generator to create unique Portfolio name
        self.pName = "Test Portfolio" + random_generator()

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
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.cm.click_settings()
        self.port.validating_name_comp()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.click_add_portfolio_manager()
        self.port.validate_add_manager()
        self.app.enter_first_name("Brandon")
        self.app.enter_last_name("Buchannan")
        self.app.enter_email(self.email)
        self.app.enter_dod_id("1230456789")
        self.app.click_next_roles()
        self.app.validate_port_permission()
        self.app.click_box_app()
        self.app.click_box_fund()
        self.app.click_box_port()
        self.app.click_save()
        self.port.validating_invite_sent()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_toggle_menu_b()
        self.app.click_edit_roles_perm_b()
        self.app.click_box_fund_remove()
        self.app.click_save_app()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success"), "Success!"
                )
            )
            self.driver.execute_script(
                set_session_status("passed", "Application Indexing Verified")
            )
        except TimeoutException:
            self.driver.execute_script(
                set_session_status("failed", "Indexing Not Verified")
            )

        print("Test: Edit Portfolio Member")
