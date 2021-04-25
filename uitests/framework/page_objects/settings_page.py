class SettingsPages:
    btn_select_portfolio_css = ".sidenav__link-label"
    btn_settings_css = "span.icon.icon--cog"

    def __init__(self, driver):
        self.driver = driver

    def select_portfolio(self):
        self.driver.find_element_by_css_selector(self.btn_select_portfolio_css).click()

    def click_settings(self):
        self.driver.find_element_by_css_selector(self.btn_settings_css).click()
