import pytest

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.settings_page import SettingsPages
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages


@pytest.mark.smoke
class TestSettings:
    url2 = ReadConfig.getLoginLocalURL()

    def test_settings(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "2. Validating Settings"}}'
        )

        # Initializing Page Objects
        self.cm = PageObjectMethods(self.driver)
        self.set = SettingsPages(self.driver)
        self.port = AddNewPortfolioPages(self.driver)

        self.cm.validate_atat()
        self.cm.validate_jedi()
        self.set.select_portfolio()
        self.cm.validate_brandon()
        self.set.click_settings()
        self.port.validating_name_comp()
        try:
            WebDriverWait(self.driver, 5).until(EC.title_contains("JEDI Cloud"))
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Title matched!"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Title not matched"}}'
            )
        print("Test: Validating Settings")
        self.driver.quit()
