import datetime
import time
import string
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.application_page import CreateApplicationPages

time_now = datetime.datetime.now().strftime("%m%d%Y%H%M%S")


class TestCreateApplication:
    url2 = ReadConfig.getLoginLocalURL()

    def test_create_application(self, setup):
        self.driver = setup
        self.driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", '
            '"arguments": {"name": "5. Create Application"}}'
        )
        self.driver.get(self.url2)
        self.driver.maximize_window()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "a.topbar__link span.topbar__link-label"), "ATAT"
            )
        )
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "header > nav > div > a:nth-child(1)"),
                "Brandon Buchannan",
            )
        )
        self.driver.execute_script(
            "document.querySelector('a.usa-button.usa-button-primary').scrollIntoView()"
        )
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.home__content"), "JEDI Cloud Services"
            )
        )
        self.app = CreateApplicationPages(self.driver)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.select_portfolio()
        time.sleep(30)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.usa-button.usa-button-primary")
            )
        ).click()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-text"),
                "Name and Describe New Application",
            )
        )
        self.app.enter_app_name(time_now + "QA App")
        self.app.enter_app_description("App description goes here")
        self.app.click_next_add_environments()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "Application Saved"
            )
        )
        self.app.click_next_add_members()
        time.sleep(10)
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.sticky-cta-text"), "Add Members"
            )
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_add_member()
        self.app.enter_first_name("Brandon")
        self.app.enter_last_name("Buchannan")
        self.email = random_generator() + "@gmail.com"
        self.app.enter_email(self.email)
        self.app.enter_dod_id("1230456789")
        self.app.click_next_roles()
        self.app.click_edit_item_box()
        self.app.click_manage_env_box()
        self.driver.execute_script(
            "document.querySelector('#environment_roles-0-role-None').value='ADMIN'"
        )
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.app.click_save_app()
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "invitation has been sent"
            )
        )
        try:
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "#application-members"), "Application Team"
                )
            )
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


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))
