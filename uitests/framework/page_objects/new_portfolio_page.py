import random
import string

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from . import PageObjectMethods


class AddNewPortfolioPages:
    btn_new_portfolio_css = "a.usa-button.usa-button-primary"
    btn_portfolio_name_css = "#name"
    portfolio_description_css = "#description"
    save_portfolio_btn_css = "input.usa-button.usa-button-primary"
    cancel_portfolio_btn_css = "usa-button usa-button-secondary"
    select_checkbox_css = ".usa-input li:nth-child(4) label"
    select_checkbox_permissions_one = "div:nth-child(1) > div > fieldset > legend > label"
    select_checkbox_permissions_two = "div:nth-child(2) > div > fieldset > legend > label"
    select_checkbox_permissions_three = "div:nth-child(3) > div > fieldset > legend > label"
    select_checkbox_permissions_four = "div:nth-child(4) > div > fieldset > legend > label"
    btn_add_port_manager = "div.portfolio-admin > div > a"
    btn_add_member_next = "div:nth-child(2) > div.action-group > input:nth-child(1)"
    btn_expand = "tr:nth-child(2) > td.toggle-menu__container > div.toggle-menu > span"
    btn_revoke = "div.toggle-menu > div > a:nth-child(3)"
    btn_revoke_invite = "div.toggle-menu > div > a:nth-child(3)"
    btn_revoke_invite_confirm = "button.action-group__action.usa-button.usa-button-primary"
    btn_confirm_revoke = "button.action-group__action.usa-button.usa-button-primary"
    btn_resend_invite = "tr:nth-child(2) > td.toggle-menu__container > div.toggle-menu > div > a:nth-child(2)"
    btn_resend_invite_b = "td.toggle-menu__container > div > div > a:nth-child(2)"
    btn_resend_invite_confirm = "//html/body/div/div[3]/div[2]/div/div/div[2]/div[2]/div[3]/div/div/div/div/form/div[2]/input"
    btn_resend_invite_confirm_b = "/html/body/div/div[3]/div[2]/div/div/div[3]/div/div[1]/div[2]/div/div/div/div/form/div[2]/input"


    def __init__(self, driver):
        self.driver = driver

    def click_new_portfolio(self):
        new_portfolio_btn = self.driver.find_element_by_css_selector(
            self.btn_new_portfolio_css
        )
        new_portfolio_btn_text = new_portfolio_btn.text
        if new_portfolio_btn_text == "Add New Portfolio":
            new_portfolio_btn.click()

    # Validating New Portfolio is displayed
    def validate_new_portfolio(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".portfolio-header__name > h1"), "New Portfolio"
            )
        )

    # Validating "Name and Describe Portfolio" is displayed
    def validate_name_desc(self):
        page_label_exists = self.driver.find_element_by_css_selector(".sticky-cta-text > h3")
        assert page_label_exists.text == "Name and Describe Portfolio"
        
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

    def click_add_portfolio_manager(self):
        self.driver.find_element_by_css_selector(self.btn_add_port_manager).click()

    def click_box_permissions_one(self):
        self.driver.find_element_by_css_selector(self.select_checkbox_permissions_one).click()

    def click_box_permissions_two(self):
        self.driver.find_element_by_css_selector(self.select_checkbox_permissions_two).click()

    def click_box_permissions_three(self):
        self.driver.find_element_by_css_selector(self.select_checkbox_permissions_three).click()

    def click_box_permissions_four(self):
        self.driver.find_element_by_css_selector(self.select_checkbox_permissions_four).click()

    def click_next_add_mem(self):
        self.driver.find_element_by_css_selector(self.btn_add_member_next).click()

    def click_expand(self):
        self.driver.find_element_by_css_selector(self.btn_expand).click()

    def click_revoke(self):
        self.driver.find_element_by_css_selector(self.btn_revoke).click()

    def click_revoke_invite(self):
        self.driver.find_element_by_css_selector(self.btn_revoke_invite).click()

    def click_revoke_invite_confirm(self):
        self.driver.find_element_by_css_selector(self.btn_revoke_invite_confirm).click()

    def click_confirm_revoke(self):
        self.driver.find_element_by_css_selector(self.btn_confirm_revoke).click()

    def click_resend_invite(self):
        self.driver.find_element_by_css_selector(self.btn_resend_invite).click()

    def click_resend_invite_b(self):
        self.driver.find_element_by_css_selector(self.btn_resend_invite_b).click()

    def click_resend_invite_confirm(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.element_to_be_clickable((By.XPATH, self.btn_resend_invite_confirm))).click()
        # self.driver.find_element(By.XPATH, self.btn_resend_invite_confirm).click()

    def click_resend_invite_confirm_b(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.element_to_be_clickable((By.XPATH, self.btn_resend_invite_confirm_b))).click()

    def validating_name_comp(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.portfolio-content > div.portfolio-admin > section > h3"),
                "Portfolio name and component"
            )
        )

    def validating_invite_sent(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > h3"),
                "Brandon Buchannan's invitation has been sent"
            )
        )

        
def random_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))
