import datetime

from uitests.framework.page_objects.common_methods import JediCommonMethods

time_now = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
time_run = 0


class ReportsPages:
    def __init__(self, driver):
        self.driver = driver

    btn_select_portfolio_css = ".sidenav__link-label"
    save_portfolio_btn_css = "input.usa-button.usa-button-primary"
    portfolio_description_css = "#description"
    btn_portfolio_name_css = "#name"
    select_checkbox_css = ".usa-input li:nth-child(4) label"
    btn_reports = "div.portfolio-header.row > div:nth-child(2) > div > a:nth-child(4)"
    btn_task_order = "div.portfolio-funding > div > div > a"
    # Main page viewing status of task orders and adding new task order
    btn_new_portfolio_css = "a.usa-button.usa-button-primary"
    select_portfolio_css = ".sidenav__link-label"
    btn_task_order_css = "a[href$='orders']"
    btn_add_to_css = "a[href$='1']"
    acc_active_to_css = ".div:nth-child(2) > div > h4 > button"
    acc_draft_to_css = ".div:nth-child(3) > div > h4 > button"
    acc_future_to_css = ".div:nth-child(4) > div > h4 > button"
    acc_expired_to_css = ".div:nth-child(5) > div > h4 > button"

    # Step 1 adding the task order document
    btn_file_browse_css = "label.upload-label"
    lnk_dummy_file_css = "a.uploaded-file__name"
    btn_cancel_css = ".action-group-footer.action-group-footer--expand-offset > div > a"
    btn_next_add_to_number_css = ".action-group-footer--container input"

    # Step 2 adding the task order number
    click_TO_number_css = ".action-group-footer--container input"
    txt_TO_number = "#number"
    btn_previous_css = "#to_form > div.action-group-footer.action-group-footer--expand-offset > div > button"
    btn_next_add_clin_css = (
        "div.action-group-footer.action-group-footer--expand-offset > div > input"
    )

    # Step 3 adding task order details: clin number, idiq type, value, obligated value, start date, end date
    txt_add_clin_number_css = "#clins-0-number"
    drpdn_idiq_css = "#clins-0-jedi_clin_type"
    txt_clin_value_css = "#clins-0-total_amount"
    txt_obligated_clin_css = "#clins-0-obligated_amount"
    txt_start_month_css = "fieldset[name='clins-0-start_date'] input[name='date-month']"
    txt_start_day_css = "fieldset[name='clins-0-start_date'] input[name='date-day']"
    txt_start_year_css = "fieldset[name='clins-0-start_date'] input[name='date-year']"
    txt_end_month_css = "fieldset[name='clins-0-end_date'] input[name='date-month']"
    txt_end_day_css = "fieldset[name='clins-0-end_date'] input[name='date-day']"
    txt_end_year_css = "fieldset[name='clins-0-end_date'] input[name='date-year']"
    btn_add_another_clin_css = "#add-clin"
    btn_next_review_TO_css = ".action-group-footer--container input[type=submit]"

    # Step 4 review changes and view TO summary
    btn_next_confirm_css = (
        ".action-group-footer--expand-offset > div > a.usa-button.usa-button-primary"
    )

    # Step 5 agree and confirm page
    box_sign_one_css = "div:nth-child(1) > div > fieldset > legend > label"
    box_sign_two_css = "div:nth-child(2) > div > fieldset > legend > label"
    btn_submit_css = "#to_form > div.action-group-footer.action-group-footer--expand-offset > div > input"

    def click_new_portfolio(self):
        new_portfolio_btn = self.driver.find_element_by_css_selector(
            self.btn_new_portfolio_css
        )
        new_portfolio_btn_text = new_portfolio_btn.text
        if new_portfolio_btn_text == "Add New Portfolio":
            new_portfolio_btn.click()

    def click_save_portfolio_btn(self):
        self.driver.find_element_by_css_selector(self.save_portfolio_btn_css).click()

    def select_portfolio(self):
        self.driver.find_element_by_css_selector(self.btn_select_portfolio_css).click()

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

    def click_reports(self):
        self.driver.find_element_by_css_selector(self.btn_reports).click()

    def click_task_order(self):
        self.driver.find_element_by_css_selector(self.btn_task_order).click()

    # def click_new_portfolio(self):
    #     self.driver.find_element_by_css_selector(self.btn_new_portfolio_css).click()
    #
    # def select_portfolio(self):
    #     self.driver.find_element_by_css_selector(self.select_portfolio_css).click()
    #
    # def click_task_order(self):
    #     self.driver.find_element_by_css_selector(self.btn_task_order_css).click()

    def click_add_new_to(self):
        self.driver.find_element_by_css_selector(self.btn_add_to_css).click()

    def click_active_to(self):
        self.driver.find_element_by_css(self.acc_active_to_css).click()

    def click_draft_to(self):
        self.driver.find_element_by_css(self.acc_draft_to_css).click()

    def click_future_to(self):
        self.driver.find_element_by_css(self.acc_future_to_css).click()

    def click_expired_to(self):
        self.driver.find_element_by_css(self.acc_expired_to_css).click()

    # Step 1 adding the task order document
    def click_cancel_css(self):
        self.driver.find_element_by_css(self.btn_cancel_css).click()

    def click_browse(self):
        self.driver.find_element_by_css_selector(self.btn_file_browse_css).click()

    def validate_dummy_file(self):
        self.driver.find_element_by_css(self.lnk_dummy_file_css).click()

    def click_next_add_TO_number(self):
        self.driver.find_element_by_css_selector(
            self.btn_next_add_to_number_css
        ).click()

    # Step 2 adding the task order number
    def enter_TO_number(self):
        self.driver.find_element_by_css_selector(self.txt_TO_number).send_keys(time_now)

    def click_previous(self):
        self.driver.find_element_by_css(self.btn_previous_css).click()

    def click_next_add_clin_number(self):
        self.driver.find_element_by_css_selector(self.btn_next_add_clin_css).click()

    # Step 3 adding task order details: clin number, idiq type, value, obligated value, start date, end date
    def enter_clin_number(self, clinNumber):
        self.driver.find_element_by_css_selector(
            self.txt_add_clin_number_css
        ).send_keys(clinNumber)

    def select_idiq_number(self):
        self.driver.find_element_by_css(self.drpdn_idiq_css).click()

    def add_clin_value(self, clinValue):
        self.driver.find_element_by_css_selector(self.txt_clin_value_css).send_keys(
            clinValue
        )

    def add_obligated_clin_value(self, obligatedValue):
        self.driver.find_element_by_css_selector(self.txt_obligated_clin_css).send_keys(
            obligatedValue
        )

    def add_start_month(self, startMonth):
        self.driver.find_element_by_css_selector(self.txt_start_month_css).send_keys(
            startMonth
        )

    def add_start_day(self, startDay):
        self.driver.find_element_by_css_selector(self.txt_start_day_css).send_keys(
            startDay
        )

    def add_start_year(self, startYear):
        self.driver.find_element_by_css_selector(self.txt_start_year_css).send_keys(
            startYear
        )

    def add_end_month(self, endMonth):
        self.driver.find_element_by_css_selector(self.txt_end_month_css).send_keys(
            endMonth
        )

    def add_end_day(self, endDay):
        self.driver.find_element_by_css_selector(self.txt_end_day_css).send_keys(endDay)

    def add_end_year(self, endYear):
        self.driver.find_element_by_css_selector(self.txt_end_year_css).send_keys(
            endYear
        )

    def click_add_another_clin(self):
        self.driver.find_element_by_css_selector(self.btn_add_another_clin_css).click()

    def click_next_review_TO(self):
        self.driver.find_element_by_css_selector(self.btn_next_review_TO_css).click()

    # Step 4 review changes and view TO summary
    def click_confirm(self):
        self.driver.find_element_by_css_selector(self.btn_next_confirm_css).click()

    # Step 5 agree and confirm page
    def click_checkbox_one(self):
        self.driver.find_element_by_css_selector(self.box_sign_one_css).click()

    def click_check_box_two(self):
        self.driver.find_element_by_css_selector(self.box_sign_two_css).click()

    def click_submit_TO(self):
        self.driver.find_element_by_css_selector(self.btn_submit_css).click()
