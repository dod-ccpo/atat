import pytest

from selenium.common.exceptions import TimeoutException
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import (
    AddNewPortfolioPages,
    random_generator,
)
from uitests.framework.page_objects.task_order_page import TaskOrderPage
from uitests.framework.page_objects import PageObjectMethods
from uitests.framework.utilities.browserstack import (
    set_session_name,
    set_session_status,
)


@pytest.mark.daily
@pytest.mark.regression
class TestToIndexEmptyState:
    url2 = ReadConfig.getLoginLocalURL()

    def test_to_index_emty_state(self, setup):
        # Setting up driver, session/test name, maximizing window
        self.driver = setup
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.driver.execute_script(
            set_session_name(" 20.TO Index Landing Page - Empty State")
        )
        # Initializing Page Objects
        self.port = AddNewPortfolioPages(self.driver)
        self.cm = PageObjectMethods(self.driver)

        # Generating random portfolio name
        self.pName = "Test Portfolio" + random_generator()

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
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        # Initializing TaskOrder page
        self.to = TaskOrderPage(self.driver)
        self.to.click_task_order()
        self.to.confirm_text_TO_exists()
        try:
            self.to.validate_add_to()
            self.driver.execute_script(
                set_session_status("passed", "Add Approved TaskOrders- Text is Matched")
            )
        except TimeoutException:
            self.driver.execute_script(
                set_session_name(
                    "failed", "Add Approved TaskOrders-Text is NOT Matched"
                )
            )
        print(self.msg)
