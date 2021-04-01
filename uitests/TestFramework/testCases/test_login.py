from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pageObjects.CommonMethods import Jedi_Common_Methods
from pageObjects.LoginPage import Login
from utilities.readProperties import ReadConfig


class Test_001_Login:
    url2 = ReadConfig.getLoginLocalURL()

    def test_user_login(self, setup):
        self.driver = setup
        self.driver.execute_script('browserstack_executor: {"action": "setSessionName", '
                                   '"arguments": {"name": "FAILED User Login"}}')
        self.driver.get(self.url2)
        self.driver.maximize_window()
        assert ("ATAT" in self.driver.page_source)
        self.login = Login(self.driver)
        self.login.userName()
        self.cm = Jedi_Common_Methods(self.driver)
        self.cm.click_Home()
        self.login.clickLogout()
        assert ("Access the JEDI Cloud" in self.driver.page_source)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h3.usa-alert-heading'),
                                                 'Loggeddddout'))
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Successfully Logged Out"}}')
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Logout Not Successful"}}')
        print(self.driver.title)
        self.driver.quit()
