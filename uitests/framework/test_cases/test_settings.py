import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.settings_page import SettingsPages


class TestSettings:
    url2 = ReadConfig.getLoginLocalURL()

    def test_settings(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "Settings"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(20)
        assert "ATAT" in self.driver.page_source
        self.set = SettingsPages(self.driver)
        self.set.select_portfolio()
        time.sleep(20)
        self.set.click_settings()
        time.sleep(20)
        assert "Portfolio name and component" in self.driver.page_source
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
        print(self.driver.title)
        self.driver.quit()
