import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.application_page import (
    CreateApplicationPages,
    random_dod_id_generator,
)
from uitests.framework.page_objects.new_portfolio_page import random_generator
from uitests.framework.page_objects.login_page import Login
from uitests.framework.utilities.read_properties import ReadConfig


@pytest.mark.AT6163
@pytest.mark.regression
class TestAddNewUser:
    url2 = ReadConfig.getLoginLocalURL()
    url = ReadConfig.getApplicationURL()

    def test_new_user(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "27. Create New User"}}'
        )

        # Initializing Page Objects
        self.login = Login(self.driver)
        self.cm = PageObjectMethods(self.driver)
        self.app = CreateApplicationPages(self.driver)

        # Generator to create unique DOD ID number
        self.dodid = random_dod_id_generator()

        # Generator to create unique email address
        self.email = random_generator() + "@gmail.com"

        self.driver.get(
            self.url
            + "/dev-new-user?first_name=Jimmy&last_name=Valentine&dod_id="
            + self.dodid
        )
        self.login.validate_new_user_name()
        self.login.validate_new_profile_notice()
        self.login.enter_email(self.email)
        self.login.enter_phone_number("(123) 456-7890")
        self.login.click_airforce()
        self.login.click_usa()
        self.login.click_foreign()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.login.click_next()
        self.login.validate_user_info_update()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.home__content"), "JEDI Cloud Services"
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Successfully Created New CCPO User"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"New CCPO User creation Not Successful"}}'
            )
        print("Test: Creation of New User")
        self.driver.quit()
