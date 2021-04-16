import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.login_page import Login
from uitests.framework.utilities.read_properties import ReadConfig


@pytest.mark.smoke
class Test_Login:
    url2 = ReadConfig.getLoginLocalURL()

    def test_user_login(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "1. Verification of User Login"}}'
        )

        # Initializing Page Objects
        self.login = Login(self.driver)
        self.cm = PageObjectMethods(self.driver)

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.login.userName()
        self.cm.click_Home()
        self.login.clickLogout()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div > div > div:nth-child(2)"), "Logged out"
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Successfully Logged Out"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Logout Not Successful"}}'
            )
        print("Test: Verification of User Login")
        self.driver.quit()
