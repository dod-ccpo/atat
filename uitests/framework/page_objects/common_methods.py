class JediCommonMethods:
    btn_home_css = "a.topbar__link.topbar__link--home"
    btn_user_css = ".topbar__link-label"
    btn_support_css = "a:nth-child(2) .topbar__link-label"
    btn_logout_css = "a:nth-child(3) span.topbar__link-label"
    btn_settings_css = "span.icon.icon--cog"
    btn_task_orders_css = "a[href$='orders']"
    btn_applications_css = "a.usa-button.usa-button-primary"

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
        self.driver.find_element_by_css_selector(self.btn_applications_css).click()
