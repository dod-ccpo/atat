from . import PageObjectMethods


class SettingsPages:
    btn_select_portfolio_css = ".sidenav__link-label"
    btn_settings_css = "span.icon.icon--cog"

    txt_portfolio_name_css = "#name"
    txt_portfolio_description_css = "#description"
    btn_save_changes_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div.portfolio-admin > section > form > div.edit-portfolio-name.action-group > button"
    btn_add_portfolio_manager_css = "#app-root > div.global-layout > div.global-panel-container > div > div > div.portfolio-content > div.portfolio-admin > div > a"

    def __init__(self, driver):
        self.driver = driver

    def select_portfolio(self):
        self.driver.find_element_by_css_selector(self.btn_select_portfolio_css).click()

    def click_settings(self):
        self.driver.find_element_by_css_selector(self.btn_settings_css).click()

    def edit_portfolio_name(self):
        self.driver.find_element_by_css(self.txt_portfolio_name_css).send_keys()

    def edit_portfolio_description(self):
        self.driver.find_element_by_css(self.txt_portfolio_description_css).send_keys()

    def click_save_button(self):
        self.driver.find_element_by_css(self.btn_save_changes_css).click()

    def click_add_portfolio_manager(self):
        self.driver.find_element_by_css(self.btn_add_portfolio_manager_css).click()
