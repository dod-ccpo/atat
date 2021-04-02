from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from uitests.framework.page_objects.common_methods import JediCommonMethods
import datetime

time_now = datetime.datetime.now().strftime("%m%d%Y%H%M%S")


class CreateApplicationPages:
    # Main Application overview page
    # btn_new_portfolio_css = "a.usa-button.usa-button-primary"
    btn_select_portfolio_css = "span.sidenav__link-label"
    btn_create_app_css = "usa-button usa-button-primary"
    btn_collapse_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div.portfolio-applications > div > div.action-group > a"
    acc_environments_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div.portfolio-applications > div > div.accordion > div:nth-child(2) > h4 > button"

    # Step 1 naming and describing the application
    txt_app_name_css = "#name"
    txt_app_description_css = "#description"
    btn_next_add_environments_css = "button.usa-button.usa-button-primary"
    btn_cancel_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > form > div.action-group-footer.action-group-footer--expand-offset > div > a"

    # Step 2 adding and editing environments
    btn_previous_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > form > div.action-group-footer.action-group-footer--expand-offset > div > a.usa-button.usa-button-secondary"
    btn_next_add_members_css = "button.usa-button.usa-button-primary"
    btn_add_other_environments_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > form > div.panel > div > div.application-list-item > div > button"
    btn_remove_env_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > form > div.panel > div > div.application-list-item > ul > li:nth-child(1) > div.application-edit__env-list-item-block > button > span.icon.icon--trash > svg > path"

    # Step 3 add members to environments
    btn_save_application_css = "input[type='submit']"
    btn_add_member_css = "div.portfolio-content > div > div.panel.form > a"
    txt_fname_css = "#user_data-first_name"
    txt_lname_css = "#user_data-last_name"
    txt_email_css = "#user_data-email"
    txt_phone_css = "#user_data-phone_number"
    txt_ext_css = "#user_data-phone_ext"
    txt_dod_id_css = "#user_data-dod_id"
    btn_special_cancel_css = (
        "#add-app-mem > div > div:nth-child(1) > div.action-group > a"
    )
    btn_next_roles_css = "input.action-group__action.usa-button"
    box_edit_team_css = "div:nth-child(1) > div > fieldset > legend > label"
    box_manage_env_css = "div:nth-child(2) > div > fieldset > legend > label"
    drpdn_dev_css = "#environment_roles-0-role-None"
    drpdn_prod_css = "#environment_roles-1-role-None"
    drpdn_stage_css = "#environment_roles-2-role-None"
    drpdn_test_css = "#environment_roles-3-role-None"
    btn_special_previous_css = "#add-app-mem > div > div:nth-child(2) > div.action-group > input.action-group__action.usa-button.usa-button-secondary"
    btn_save_css = (
        "#add-app-mem > div > div:nth-child(2) > div.action-group > input:nth-child(1)"
    )

    # Step 4 review, save, and add/or more team members
    btn_save_app_css = (
        "#add-app-mem > div > div:nth-child(2) > div.action-group > input:nth-child(1)"
    )
    btn_add_other_member_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > div.panel.form > a"
    acc_options_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > div.panel.form > section > div > table > tbody > tr > td.toggle-menu__container > div > span"
    acc_roles_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > div.panel.form > section > div > table > tbody > tr > td.toggle-menu__container > div > div > a:nth-child(1)"
    acc_resend_invite_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > div.panel.form > section > div > table > tbody > tr > td.toggle-menu__container > div > div > a:nth-child(1)"
    acc_revoke_invite_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div > div.panel.form > section > div > table > tbody > tr > td.toggle-menu__container > div > div > a:nth-child(1)"

    def __init__(self, driver):
        self.driver = driver

    # Main page viewing status application and creating an application
    # def click_new_portfolio(self):
    # self.driver.find_element_by_css_selector(self.btn_new_portfolio_css).click()

    def select_portfolio(self):
        # wait = WebDriverWait(self.driver, 20)
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.btn_select_portfolio_css))).click()
        self.driver.find_element_by_css_selector(self.btn_select_portfolio_css).click()

    def click_create_app(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.btn_create_app_css))
        ).click()
        # self.driver.find_element_by_css_selector(self.btn_create_app_css).click()

    def click_collapse(self):
        self.driver.find_element_by_css(self.btn_collapse_css).click()

    def click_environment_acc(self):
        self.driver.find_element_by_css(self.acc_environments_css).click()

    # Step 1 naming and describing the application
    def enter_app_name(self,appName):
        self.driver.find_element_by_css_selector(self.txt_app_name_css).send_keys(appName)

    def enter_app_description(self,description):
        self.driver.find_element_by_css_selector(self.txt_app_description_css).send_keys(description)

    def click_next_add_environments(self):
        self.driver.find_element_by_css_selector(
            self.btn_next_add_environments_css
        ).click()

    def click_cancel(self):
        self.driver.find_element_by_css(self.btn_cancel_css).click()

    # Step 2 adding and editing environments
    def click_previous(self):
        self.driver.find_element_by_css(self.btn_previous_css).click()

    def click_next_add_members(self):
        self.driver.find_element_by_css_selector(self.btn_next_add_members_css).click()

    def click_add_other_env(self):
        self.driver.find_element_by_css(self.btn_add_other_environments_css).click()

    def click_remove_env(self):
        self.driver.find_element_by_css(self.btn_remove_env_css).click()

    # Step 3 add members to environments
    def click_save_app(self):
        self.driver.find_element_by_css_selector(self.btn_save_application_css).click()

    def click_add_member(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.btn_add_member_css))
        ).click()
        # self.driver.find_element_by_css_selector(self.btn_add_member_css).click()

    def enter_first_name(self,fName):
        self.driver.find_element_by_css_selector(self.txt_fname_css).send_keys(fName)

    def enter_last_name(self,lName):
        self.driver.find_element_by_css_selector(self.txt_lname_css).send_keys(lName)

    def enter_email(self,email):
        self.driver.find_element_by_css_selector(self.txt_email_css).send_keys(email)

    def enter_phone_number(self,phone):
        self.driver.find_element_by_css_selector(self.txt_phone_css).send_keys()

    def enter_extension(self):
        self.driver.find_element_by_css(self.txt_ext_css).send_keys()

    def enter_dod_id(self,dodID):
        self.driver.find_element_by_css_selector(self.txt_dod_id_css).send_keys(dodID)

    def click_special_cancel(self):
        self.driver.find_element_by_css(self.btn_special_cancel_css).click()

    def click_next_roles(self):
        self.driver.find_element_by_css_selector(self.btn_next_roles_css).click()

    def click_edit_item_box(self):
        self.driver.find_element_by_css_selector(self.box_edit_team_css).click()

    def click_manage_env_box(self):
        self.driver.find_element_by_css_selector(self.box_manage_env_css).click()

    def select_development(self):
        self.driver.find_element_by_css_selector(self.drpdn_dev_css).click()

    def select_production(self):
        self.driver.find_element_by_css(self.drpdn_prod_css).click()

    def select_staging(self):
        self.driver.find_element_by_css(self.drpdn_stage_css).click()

    def select_testing(self):
        self.driver.find_element_by_css(self.drpdn_test_css).click()

    def click_special_previous(self):
        self.driver.find_element_by_css(self.btn_special_previous_css).click()

    def click_save(self):
        self.driver.find_element_by_css(self.btn_save_css).click()

    # Step 4 review, save, and add/or more team members
    def click_save_application(self):
        self.driver.find_element_by_css(self.btn_save_app_css).click()

    def click_add_other_members(self):
        self.driver.find_element_by_css(self.btn_add_other_member_css).click()

    def select_options(self):
        self.driver.find_element_by_css(self.acc_options_css).click()

    def select_roles(self):
        self.driver.find_element_by_css(self.acc_roles_css).click()

    def select_resend_invite(self):
        self.driver.find_element_by_css(self.acc_resend_invite_css).click()

    def select_revoke_invite(self):
        self.driver.find_element_by_css(self.acc_revoke_invite_css).click()
