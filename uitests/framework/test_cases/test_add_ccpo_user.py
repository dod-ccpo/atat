import pytest
import random
import string

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.login_page import Login
from uitests.framework.utilities.read_properties import ReadConfig


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
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "34. Verification of New CCPO User"}}'
        )

        # Initializing Page Objects
        self.login = Login(self.driver)
        self.cm = PageObjectMethods(self.driver)

        # Generator to create unique DOD ID number
        self.dodid = random_no_generator()

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
                    "Sam Stevenson",
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
        print("Test: Verification of New CCPO User")
        self.driver.quit()


def random_no_generator(size=10, chars=string.digits):
    return "".join(random.choice(chars) for x in range(size))
