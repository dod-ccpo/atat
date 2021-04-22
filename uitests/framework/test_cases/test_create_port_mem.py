import pytest
import random
import string

from selenium.common.exceptions import TimeoutException
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.page_objects.application_page import CreateApplicationPages
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

current_dir_path = "./uitests/framework/resources/test.pdf"


@pytest.mark.regression
class TestNewPortMem:
    url2 = ReadConfig.getLoginLocalURL()

    def test_new_port_mem(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "32. Create New Portfolio Member"}}'
        )

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
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > h3"), "Brandon Buchannan's invitation has been sent"
                )
            )
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Application Indexing Verified"}}'
            )
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Indexing Not Verified"}}'
            )

        print("Test: Create New Portfolio Member")
        self.driver.quit()

def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))