import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.login_page import Login
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.utilities.browserstack import (
    set_session_name,
    set_session_status,
)


@pytest.mark.AT6163
@pytest.mark.regression
class TestAddNewCcpoUser:
    url2 = ReadConfig.getLoginLocalURL()
    url = ReadConfig.getApplicationURL()

    def test_new_ccpo_user(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url)
        self.driver.get(self.url + "/login-local?username=sam")
        self.driver.maximize_window()
        self.driver.get(self.url + "/ccpo-users")
        self.driver.execute_script(
            set_session_name("34. Verification of New CCPO User")
        )

        # Initializing Page Objects
        self.login = Login(self.driver)
        self.cm = PageObjectMethods(self.driver)

        self.login.validate_ccpo_user_displayed()
        self.login.click_add_new_user()
        self.login.enter_new_dod_id("3456789012")
        self.login.click_confirm_add_user()
        self.login.validate_confirm_displayed()
        self.login.click_confirm_add_user()
        self.login.validate_confirm_page()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(1)"),
                    "Brandon Buchannan",
                )
            )
            self.driver.execute_script(
                set_session_status("passed", "Successfully created new CCPO user")
            )
        except TimeoutException:
            self.driver.execute_script(
                set_session_status(
                    "failed", "New CCPO user creation was not successful"
                )
            )
        print("Test: Verification of New CCPO User")
