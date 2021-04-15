from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class PageObjectMethods:
    btn_home_css = "a.topbar__link.topbar__link--home"
    btn_user_css = ".topbar__link-label"
    btn_support_css = "a:nth-child(2) .topbar__link-label"
    btn_logout_css = "a:nth-child(3) span.topbar__link-label"
    btn_settings_css = "a:nth-child(1) > div > div.icon-link--icon"
    btn_task_orders_css = "a[href$='orders']"
    btn_applications_css = "a:nth-child(3) > div > div.icon-link--icon"

    def __init__(self, driver):
        self.driver = driver

    def click_Home(self):
        self.driver.find_element_by_css_selector(self.btn_home_css).click()

    def click_user(self):
        self.driver.find_element_by_css_selector(self.btn_user_css).click()

    def click_support(self):
        self.driver.find_element_by_css_selector(self.btn_support_css).click()

    def click_logout(self):
        self.driver.find_element_by_css_selector(self.btn_logout_css).click()

    def click_settings(self):
        self.driver.find_element_by_css_selector(self.btn_settings_css).click()

    def click_task_order(self):
        self.driver.find_element_by_css_selector(self.btn_task_orders_css).click()

    def click_application(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.btn_applications_css))
        ).click()
        # self.driver.find_element_by_css_selector(self.btn_applications_css).click()

    # Validating ATAT is displayed
    def validate_atat(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "a.topbar__link span.topbar__link-label"), "ATAT"
            )
        )

    # Validating JEDI Cloud Services is displayed
    def validate_jedi(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "div.home__content"), "JEDI Cloud Services"
            )
        )

    # Validating "Settings" tab is displayed
    def validate_settings_tab(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div:nth-child(2) > div > a:nth-child(1) > div > div.icon-link--name",
                ),
                "Settings",
            )
        )
    
    def validate_brandon(self):
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "header > nav > div > a:nth-child(1)"),
                "Brandon Buchannan",
            )
        )
