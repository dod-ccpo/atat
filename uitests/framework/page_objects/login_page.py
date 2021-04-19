from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from . import PageObjectMethods


class Login:
    button_login_xpath = ""
    link_logout_css = "a[title*='Log out']"
    userName_css = ".topbar__context a"
    btn_new_ccpo_user = "div.global-panel-container > div > a"
    txt_dod_id = "#dod_id"
    btn_confirm_add_new_user = "input[type='submit']"
    btn_next = "input[type='submit']"

    def __init__(self, driver):
        self.driver = driver

    def clickLogin(self):
        self.driver.find_element_by_xpath(self.button_login_xpath).click()

    def userName(self):
        userName = self.driver.find_element_by_css_selector(self.userName_css)
        userName_text = userName.text
        if userName_text == "Brandon Buchannan":
            return userName_text

    def clickLogout(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.link_logout_css))
        ).click()
    
    # New CCPO User functions
    def click_add_new_user(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.btn_new_ccpo_user))
        ).click()

    def validate_ccpo_user_displayed(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.global-panel-container > div > div.col > div"), "CCPO Users",
            )
        )
    
    def enter_new_dod_id(self, dodid):
        self.driver.find_element_by_css_selector(self.txt_dod_id).send_keys(dodid)

    def click_confirm_add_user(self):
        self.driver.find_element_by_css_selector(self.btn_confirm_add_new_user).click()

    def click_next(self):
        self.driver.find_element_by_css_selector(self.btn_next).click()

    def validate_confirm_displayed(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.global-panel-container > div > h3"), "Confirm new CCPO user",
            )
        )
    
    def validate_confirm_page(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > p"), "You have successfully given Brandon Buchannan CCPO permissions.",
            )
        )