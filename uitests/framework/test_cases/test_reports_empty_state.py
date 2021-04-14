import random
import string
import time
import pytest
from selenium.common.exceptions import TimeoutException
from uitests.framework.utilities.read_properties import ReadConfig
from uitests.framework.page_objects.new_portfolio_page import AddNewPortfolioPages
from uitests.framework.page_objects.reports_page import ReportsPages


@pytest.mark.regression
class TestReportsEmptyState:
    url2 = ReadConfig.getLoginLocalURL()

    def test_reports_empty_state(self, setup):
        self.driver = setup
        self.driver.execute_script('browserstack_executor: {"action": "setSessionName", '
                                   '"arguments": {"name": "10.Verifying the Reports with no Task Orders"}}')
        self.driver.get(self.url2)
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        assert "ATAT" in self.driver.page_source
        self.port = AddNewPortfolioPages(self.driver)
        self.port.click_new_portfolio()
        self.port.validate_new_portfolio()
        self.port.validate_name_desc()
        self.pName = "Test Portfolio" + random_generator()
        self.port.enter_portfolio_name(self.pName)
        self.port.enter_portfolio_description("Entering the description to verify the text")
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.port.select_checkbox()
        self.port.click_save_portfolio_btn()
        self.msg = self.driver.find_element_by_tag_name("h1").text
        assert self.pName == self.msg
        print(self.msg)
        self.rep = ReportsPages(self.driver)
        self.rep.click_reports()
        self.rep.report_page_is_displayed()
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.rep.msg_insuf_funds()
        tpv = "$0.00"
        self.rep.total_portfolio_value(tpv)
        days = "0 days"
        self.rep.days_remaining(days)
        # verifying the Obligated funds
        ofunds = "0.00"
        self.rep.ob_funds(ofunds)
        self.rep.invoiced_exp_funds()
        try:
            # Estimated Expended funds
            self.rep.estimated_funds()
            # Remaining funds
            rfunds = "$-2.00"
            self.rep.remaining_funds(rfunds)
        except TimeoutException:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": '
                '"Timed out due to Estimated Expended funds & Remaining funds not matched "}}'
            )
        else:
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": '
                '"Estimated Expended funds & Remaining funds matched"}}'
            )
        self.driver.quit()


def random_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
