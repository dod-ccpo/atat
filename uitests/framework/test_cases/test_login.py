from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from page_objects.common_methods import JediCommonMethods
from page_objects.login_page import Login
from utilities.read_properties import ReadConfig


class TestLogin:
    url2 = ReadConfig.getLoginLocalURL()

    def test_user_login(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "1. Verification of User Login"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "a.topbar__link span.topbar__link-label"), "ATAT"
            )
        )
        self.login = Login(self.driver)
        self.login.userName()
        self.cm = JediCommonMethods(self.driver)
        self.cm.click_Home()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.home__content"), "JEDI Cloud Services"
            )
        )
        self.login.clickLogout()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "h3.usa-alert-heading"), "Logged out"
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
        print(self.driver.title)
        self.driver.quit()
