import random
import string
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utilities.readProperties import ReadConfig
from pageObjects.NewPortfolioPage import AddNewPortfolioPages


class Test_003_Create_Portfolio:
    url2 = ReadConfig.getLoginLocalURL()

    def test_create_portfolio(self, setup):
        self.driver = setup
        # self.driver.execute_script('browserstack_executor: {"action": "setSessionName", '
        #                            '"arguments": {"name": "Create Portfolio"}}')
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        assert ("ATAT" in self.driver.page_source)
        self.port = AddNewPortfolioPages(self.driver)
        self.port.click_new_portfolio()
        time.sleep(20)
        assert ("Name and Describe Portfolio" in self.driver.page_source)
        assert ("New Portfolio" in self.driver.page_source)
        self.pName = "Test Portfolio" + random_generator()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description("Entering the description to verify the text")
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        # assert ("Add approved task orders" in self.driver.page_source)
        #verifying the PortfolioName on the TaskOrderview
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        try:
            WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h3'),
                                                                                 'Task Orders'))
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Text is Matched"}}')
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Text is NOT Matched"}}')
        print('Task Orders')
        self.driver.quit()


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
