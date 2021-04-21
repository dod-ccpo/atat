from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class ReportsPages:
    def __init__(self, driver):
        self.driver = driver

    btn_expired_funding_css = (
        "button.usa-accordion-button"  # changed due to css selector not working
    )
    btn_reports_css = ".icon.icon--chart-pie"
    btn_reports = "div.portfolio-header.row > div:nth-child(2) > div > a:nth-child(4)"
    btn_task_order = "div.portfolio-funding > div > div > a"
    txt_TO_number = "#number"

    def click_reports(self):
        self.driver.find_element_by_css_selector(self.btn_reports).click()

    # Verifying the Reports page displayed
    def report_page_is_displayed(self):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-text > h3"), "Reports",
            )
        )

    # Verify this messages shows only if there is no Active TaskOrder for the Portfolio
    def msg_insuf_funds(self):
        msg = "Insufficient Funds"
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), msg,
            )
        )

    # Verifying the total Portfolio Value
    def total_portfolio_value(self, tpv):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    ".row > .col.col--grow.summary-item:nth-of-type(1) > .summary-item__value",
                ),
                tpv,
            )
        )

    # verify the Days Remaining
    def days_remaining(self, days):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    ".row > .col.col--grow.summary-item:nth-of-type(3) > .summary-item__value",
                ),
                days,
            )
        )

    # verifying the Obligated funds
    def ob_funds(self, ofunds):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.jedi-clin-funding__clin-wrapper > h3"), ofunds,
            )
        )

    # verifying the Invoiced Expended funds
    def invoiced_exp_funds(self):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(1) > p.h3.jedi-clin-funding__meta-value",
                ),
                "$1.00",
            )
        )

    # Verifying the Estimated funds
    def estimated_funds(self):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(2) > p.h3.jedi-clin-funding__meta-value",
                ),
                "$1.00",
            )
        )

    # Remaining funds
    def remaining_funds(self, rfunds):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(3) > p.h3.jedi-clin-funding__meta-value",
                ),
                rfunds,
            )
        )

    # verifying the Active TO title
    def active_to_text(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.h4"), "Active Task Orders",
            )
        )

    # verifying the Active TaskOrder details
    def active_task_order_number(self, tno):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.jedi-clin-funding__active-task-orders > a",), tno
            )
        )

    # Click on the Active TO Link
    def active_to_link(self):
        to_link = self.driver.find_element_by_css_selector(
            "div.jedi-clin-funding__active-task-orders > a")
        self.driver.execute_script("arguments[0].click();", to_link)

    # By clicking on the link,Verify on TaskOrder #-TO Follow Link
    def valid_to_no_display(self, taskorderno):
        WebDriverWait(self.driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-text > h3"), taskorderno,
            )
        )

    # Validation on TO Follow Link-TotalValue
    def total_value(self, totalvalue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".usa-grid > .summary-item:nth-of-type(1) > .summary-item__value--large"), totalvalue,
            )
        )

    # Validation on TO Follow Link-TotalObligated value
    def total_ob(self, totalob):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".usa-grid > .summary-item:nth-of-type(2) > .summary-item__value--large"), totalob,
            )
        )

    # click on Expired Funding
    def expired_funding_click(self):
        element = self.driver.find_element_by_css_selector(
            self.btn_expired_funding_css)
        self.driver.execute_script("arguments[0].click();", element)
        # commenting the below code since it is not working on IE added JS executor
        # self.driver.find_element_by_css_selector(self.btn_expired_funding_css).click()

    # verify the TO# number under expired funding
    def expired_to_details(self, extonumber):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#expired_funding > tbody > tr:nth-of-type(1) > td"),
                extonumber,
            )
        )

    # verifying PoP under Expired funding
    def pop(self, periodofperformance):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#expired_funding > tbody > tr:nth-of-type(2) > td:nth-of-type(2)",
                ),
                periodofperformance,
            )
        )

    # verifying Amount Obligated under Expired funding
    def amount_obligated(self, amountOb):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#expired_funding > tbody > tr:nth-of-type(2) > td.table-cell--align-right:nth-of-type(4)",
                ),
                amountOb,
            )
        )

    # Below should not be included here it should be in the TaskOrder pageObjects
    # def enter_TO_number(self, tnumber):
    # self.driver.find_element_by_css_selector(self.txt_TO_number).send_keys(tnumber)
