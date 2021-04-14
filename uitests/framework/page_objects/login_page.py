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
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.link_logout_css))
        ).click()