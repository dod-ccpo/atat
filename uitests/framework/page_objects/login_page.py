from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Login:
    link_logout_css = "a[title*='Log out']"
    userName_css = ".topbar__context a"
    btn_new_ccpo_user = "div.global-panel-container > div > a"
    txt_dod_id = "#dod_id"
    btn_confirm_add_new_user = "input[type='submit']"
    btn_next = "button[type='submit']"
    btn_foreign = "#designation > li:nth-child(2) > label"
    btn_usa = "#citizenship > li:nth-child(1) > label"
    drpdn_air_force = "#service_branch > option:nth-child(2)"
    txt_email = "#email"
    txt_phone = "#phone_number"

    def __init__(self, driver):
        self.driver = driver

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
                (By.CSS_SELECTOR, "div.global-panel-container > div > div.col > div"),
                "CCPO Users",
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
                (By.CSS_SELECTOR, "div.global-panel-container > div > h3"),
                "Confirm new CCPO user",
            )
        )

    def validate_confirm_page(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > p"),
                "You have successfully given Brandon Buchannan CCPO permissions.",
            )
        )
    
    def validate_confirm_page_sam(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.usa-alert.usa-alert-success > div > p"),
                "You have successfully given Sam Stevenson CCPO permissions.",
            )
        )

    def validate_new_user_name(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.panel > div > h1 > div.h2"), "Jimmy Valentine",
            )
        )

    def validate_new_profile_notice(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"),
                "You must complete your profile",
            )
        )

    def validate_user_info_update(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"), "User information updated.",
            )
        )

    def click_foreign(self):
        self.driver.find_element_by_css_selector(self.btn_foreign).click()

    def click_usa(self):
        self.driver.find_element_by_css_selector(self.btn_usa).click()

    def click_airforce(self):
        self.driver.find_element_by_css_selector(self.drpdn_air_force).click()

    def enter_email(self, email):
        self.driver.find_element_by_css_selector(self.txt_email).send_keys(email)

    def enter_phone_number(self, phone):
        self.driver.find_element_by_css_selector(self.txt_phone).send_keys(phone)
