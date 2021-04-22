from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class CreateApplicationPages:
    btn_select_portfolio_css = "span.sidenav__link-label"
    btn_create_app_css = "div.portfolio-applications > div > div > a"
    btn_application = "a:nth-child(3) > div > div.icon-link--icon"
    txt_app_name_css = "#name"
    txt_app_description_css = "#description"
    btn_next_add_environments_css = "button.usa-button.usa-button-primary"
    btn_add_team_member = "div.panel.form > a"
    btn_next_add_members_css = "button.usa-button.usa-button-primary"
    btn_remove_env_css = "div.form-col.form-col--third > label"
    btn_save_application_css = "input[type='submit']"
    btn_save_application_next_css = "div.action-group-footer.action-group-footer--expand-offset > div > a:nth-child(1)"
    btn_add_member_css = "div.portfolio-content > div > div.panel.form > a"
    txt_fname_css = "#user_data-first_name"
    txt_lname_css = "#user_data-last_name"
    txt_email_css = "#user_data-email"
    txt_dod_id_css = "#user_data-dod_id"
    btn_next_roles_css = "input.action-group__action.usa-button"  #used 2x 
    box_edit_team_css = "div:nth-child(1) > div > fieldset > legend > label"
    box_manage_env_css = "div:nth-child(2) > div > fieldset > legend > label"
    btn_save_css = "div:nth-child(2) > div.action-group > input:nth-child(1)"
    btn_toggle_menu_css = "div.toggle-menu > span"
    btn_toggle_menu_b_css = "tr:nth-child(2) > td.toggle-menu__container > div.toggle-menu > span"
    btn_role_perm = "div.toggle-menu > div > a:nth-child(1)"
    btn_role_perm_b = "tr:nth-of-type(2) > td.toggle-menu__container > .toggle-menu > .accordion-table__item-toggle-content.toggle-menu__toggle > a:nth-of-type(1)"
    btn_save_revoke_css = "input[type='submit']"
    box_edit_app = "div:nth-child(2) > div.member-form > div > div:nth-child(1) > div > fieldset > legend > label"
    box_edit_fund = "div:nth-child(2) > div.member-form > div > div:nth-child(2) > div > fieldset > legend > label"
    box_edit_port = "div:nth-child(2) > div.member-form > div > div:nth-child(3) > div > fieldset > legend > label"
    box_edit_fund_remove = ".portfolio-perms > div:nth-of-type(2) > .usa-input.input__inline-fields.checked > fieldset.usa-input__choices > legend > label"

    def __init__(self, driver):
        self.driver = driver

    def select_portfolio(self): ###Needs to be moved to new portfolio page objects
        self.driver.find_element_by_css_selector(self.btn_select_portfolio_css).click()

    def click_create_app(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.btn_create_app_css))
        ).click()

    def click_applications(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.btn_application))
        ).click()

    def enter_app_name(self, appName):
        self.driver.find_element_by_css_selector(self.txt_app_name_css).send_keys(
            appName
        )

    def enter_app_description(self, description):
        self.driver.find_element_by_css_selector(
            self.txt_app_description_css
        ).send_keys(description)

    def click_next_add_environments(self):
        self.driver.find_element_by_css_selector(
            self.btn_next_add_environments_css
        ).click()

    def click_next_add_members(self):
        self.driver.find_element_by_css_selector(self.btn_next_add_members_css).click()

    def click_save_app(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, self.btn_save_application_css)
            )
        ).click()

    def click_save_app_next(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, self.btn_save_application_next_css)
            )
        ).click()

    def click_add_member(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.btn_add_member_css))
        ).click()

    def click_add_team_member(self):
        self.driver.find_element_by_css_selector(self.btn_add_team_member).click()

    def enter_first_name(self, fName):
        self.driver.find_element_by_css_selector(self.txt_fname_css).send_keys(fName)

    def enter_last_name(self, lName):
        self.driver.find_element_by_css_selector(self.txt_lname_css).send_keys(lName)

    def enter_email(self, email):
        self.driver.find_element_by_css_selector(self.txt_email_css).send_keys(email)

    def enter_dod_id(self, dodID):
        self.driver.find_element_by_css_selector(self.txt_dod_id_css).send_keys(dodID)

    def click_next_roles(self):
        self.driver.find_element_by_css_selector(self.btn_next_roles_css).click()

    def click_edit_item_box(self):
        self.driver.find_element_by_css_selector(self.box_edit_team_css).click()

    def click_manage_env_box(self):
        self.driver.find_element_by_css_selector(self.box_manage_env_css).click()

    def click_save(self):
        self.driver.find_element_by_css_selector(self.btn_save_css).click()

    def click_toggle_menu(self):
        self.driver.find_element_by_css_selector(self.btn_toggle_menu_css).click()

    def click_toggle_menu_b(self):
        self.driver.find_element_by_css_selector(self.btn_toggle_menu_b_css).click()

    def click_edit_roles_perm(self):
        self.driver.find_element_by_css_selector(self.btn_role_perm).click()
    
    def click_edit_roles_perm_b(self):
        self.driver.find_element_by_css_selector(self.btn_role_perm_b).click()

    def click_revoke_env(self):
        self.driver.find_element_by_css_selector(self.btn_remove_env_css).click()

    def click_save_revoke_env(self):
        self.driver.find_element_by_css_selector(self.btn_save_revoke_css).click()

    def click_box_app(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.box_edit_app))).click()

    def click_box_port(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.box_edit_port))).click()

    def click_box_fund(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.box_edit_fund))).click()    
    
    def click_box_fund_remove(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.box_edit_fund_remove))).click()   

    def click_create_application(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.usa-button.usa-button-primary")
            )
        ).click()

    def click_acc(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div:nth-child(2) > h4 > button")
            )
        ).click() 

    def validate_app_save(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "Application Saved"
            )
        )

    def validate_env_access(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#members-env-access-role"), "Environment Access"
            )
        )

    def validate_invite_pending(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "tr:nth-child(2) > td:nth-child(1) > span"),
                "INVITE PENDING",
            )
        )

    def validate_port_invite_revoke(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > h3"),
                "Portfolio invitation revoked",
            )
        )

    def validate_name_desc(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-text"),
                "Name and Describe New Application",
            )
        )

    def validate_revoke_warning(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.form-col.form-col--two-thirds > p"),
                "Save changes to revoke access, this can not be undone.",
            )
        )

    def validate_name_brandon(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "header > nav > div > a:nth-child(1)"),
                "Brandon Buchannan",
            )
        )

    def validate_add_members(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.sticky-cta-text"), "Add Members"
            )
        )

    def validate_invite_sent(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "invitation has been sent"
            )
        )
    
    def validate_acc_dev(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".usa-accordion-content > .accordion__content--list-item:nth-of-type(1) > .row > .col.col--grow")
            )
        )

    def validate_acc_prod(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".usa-accordion-content > .accordion__content--list-item:nth-of-type(2) > .row > .col.col--grow")
            )
        )

    def validate_acc_stage(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".usa-accordion-content > .accordion__content--list-item:nth-of-type(3) > .row > .col.col--grow")
            )
        )
    
    def validate_acc_test(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".usa-accordion-content > .accordion__content--list-item:nth-of-type(4) > .row > .col.col--grow")
            )
        )

    def validate_name_access(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.member-form > h2"), "Application Permissions"
            )
        )
    
    def validate_port_permission(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div > div:nth-child(2) > div.member-form > h2"), "Set Portfolio Permissions"
            )
        )

