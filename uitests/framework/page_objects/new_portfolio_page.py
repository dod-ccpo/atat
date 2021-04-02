import random
import string

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from uitests.framework.page_objects.common_methods import JediCommonMethods


class AddNewPortfolioPages:
    btn_new_portfolio_css = "a.usa-button.usa-button-primary"
    btn_portfolio_name_css = "#name"
    portfolio_description_css = "#description"
    save_portfolio_btn_css = "input.usa-button.usa-button-primary"
    cancel_portfolio_btn_css = "usa-button usa-button-secondary"
    select_checkbox_css = ".usa-input li:nth-child(4) label"

    def __init__(self, driver):
        self.driver = driver

    def click_new_portfolio(self):
        new_portfolio_btn = self.driver.find_element_by_css_selector(
            self.btn_new_portfolio_css
        )
        new_portfolio_btn_text = new_portfolio_btn.text
        if new_portfolio_btn_text == "Add New Portfolio":
            new_portfolio_btn.click()

    def enter_portfolio_name(self, pName):
        self.driver.find_element_by_css_selector(self.btn_portfolio_name_css).send_keys(
            pName
        )

    def enter_portfolio_description(self, description):
        self.driver.find_element_by_css_selector(
            self.portfolio_description_css
        ).send_keys(description)

    def select_checkbox(self):
        self.driver.find_element_by_css_selector(self.select_checkbox_css).click()

    def click_save_portfolio_btn(self):
        self.driver.find_element_by_css_selector(self.save_portfolio_btn_css).click()
        # saveBtn = self.driver.find_element_by_css_selector(self.save_portfolio_btn_css)
        # saveBtn_text = saveBtn.text
        # if saveBtn_text == 'Save Portfolio':
        #     saveBtn.click()

    def click_cancel_portfolio_btn(self):
        self.driver.find_element_by_css(self.cancel_portfolio_btn_css).click()


def random_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))
