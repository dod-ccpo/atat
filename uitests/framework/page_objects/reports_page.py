import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from uitests.framework.page_objects.task_order_page import time_run

time_now = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
time_run = 0


class ReportsPages:
    def __init__(self, driver):
        self.driver = driver

    btn_expired_funding_css = "#expired_funding"
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

    # verifying the Active TaskOrder details
    def active_task_order(self):
        tmp = str(time_run)
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.jedi-clin-funding__active-task-orders > a",), tmp
            )
        )

    # click on Expired Funding
    def expired_funding(self):
        self.driver.find_element_by_css_selector(self.btn_expired_funding_css).click()

    def enter_TO_number(self):
        self.driver.find_element_by_css_selector(self.txt_TO_number).send_keys(
            time_now)