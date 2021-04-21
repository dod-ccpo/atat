import datetime
import random
import string

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

time_run = 0


class TaskOrderPage:
    # Main page viewing status of task orders and adding new task order
    btn_new_portfolio_css = "a.usa-button.usa-button-primary"
    select_portfolio_css = ".sidenav__link-label"
    btn_task_order_css = "a[href$='orders']"
    btn_add_to_css = "a[href$='1']"
    acc_active_to_css = "div:nth-child(2) > div > h4 > button"
    acc_draft_to_css = "div:nth-child(3) > div > h4 > button"
    acc_future_to_css = "div:nth-child(4) > div > h4 > button"
    acc_expired_to_css = "div:nth-child(5) > div > h4 > button"

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
    btn_save_later_css = ".usa-button.usa-button-primary:nth-of-type(2)"
    # Step 3 adding task order details: clin number, idiq type, value, obligated value, start date, end date
    txt_add_clin_number_css = "#clins-0-number"
    drpdn_idiq_css = "#clins-0-jedi_clin_type"
    drpdn1_idiq_css = "#clins-1-jedi_clin_type"
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

    def __init__(self, driver):
        self.driver = driver

    # Verifying the Text "TaskOrders" exists on Task Order page:
    def confirm_text_TO_exists(self):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-text > h3"), "Task Orders"
            )
        )

    # Validating "Add approved task orders" is displayed in step1 workflow:
    def validate_add_to(self):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".empty-state > h3"), "Add approved task orders"
            )
        )

    # Click on the TaskOrder Tab
    def click_task_order(self):
        self.driver.find_element_by_css_selector(
            self.btn_task_order_css).click()

    # Click on the Add New TaskOrder Button
    def click_add_new_to(self):
        self.driver.find_element_by_css_selector(self.btn_add_to_css).click()

    # Step 1 adding the task order document
    def click_cancel_css(self):
        self.driver.find_element_by_css(self.btn_cancel_css).click()

    def click_browse(self):
        self.driver.find_element_by_css_selector(
            self.btn_file_browse_css).click()

    def validate_dummy_file(self):
        self.driver.find_element_by_css(self.lnk_dummy_file_css).click()

    def click_next_add_TO_number(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.btn_next_add_to_number_css)
            )
        ).click()
        # self.driver.find_element_by_css_selector(self.btn_next_add_to_number_css).click()

    # Step 2 adding the task order number
    def cancel_btn_on_add_to(self):
        self.driver.find_element_by_css_selector(
            "a.action-group__action").click()

    def save_later_yes_btn(self):
        self.driver.find_element_by_css_selector(
            self.btn_save_later_css).click()

    def enter_TO_number(self, tnumber):
        self.driver.find_element_by_css_selector(
            self.txt_TO_number).send_keys(tnumber)

    def click_previous(self):
        self.driver.find_element_by_css(self.btn_previous_css).click()

    def click_next_add_clin_number(self):
        self.driver.find_element_by_css_selector(
            self.btn_next_add_clin_css).click()

    # Step 3 adding task order details: clin number, idiq type, value, obligated value, start date, end date
    def enter_clin_number(self, clinNumber):
        self.driver.find_element_by_css_selector(
            self.txt_add_clin_number_css
        ).send_keys(clinNumber)

    # Step 3 Validating the clin header
    def clin_card_title(self, clinNumber):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".card__title > .h4"),
                clinNumber,
            )
        )

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

    def percent_obligated(self, percentObligated):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#percent-obligated"),
                percentObligated,
            )
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
        self.driver.find_element_by_css_selector(
            self.txt_end_day_css).send_keys(endDay)

    def add_end_year(self, endYear):
        self.driver.find_element_by_css_selector(self.txt_end_year_css).send_keys(
            endYear
        )

    # Step3 addingTO:Adding another clin:clin number, idiq type, value, obligated value, start date, end date
     # Validate Click Add Another Clin btn exists
    def validate_add_clin_btn(self):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#add-clin"),
                "Add Another CLIN",
            )
        )

    # Adding another clin by clicking on the ADD Another CLIN link
    def click_add_another_clin(self):
        self.driver.find_element_by_css_selector(
            self.btn_add_another_clin_css).click()

    def enter_clin_number2(self, clinNumber1):
        self.driver.find_element_by_css_selector(
            "#clins-1-number"
        ).send_keys(clinNumber1)

    def select_idiq_number2(self):
        self.driver.find_element_by_css_selector(
            "#clins-1-jedi_clin_type [value='JEDI_CLIN_2']").click()

    def add_total_clin2_value(self, clinValue2):
        self.driver.find_element_by_css_selector("#clins-1-total_amount").send_keys(
            clinValue2
        )

    def add_obligated_clin2_value(self, obligatedValue2):
        self.driver.find_element_by_css_selector("#clins-1-obligated_amount").send_keys(
            obligatedValue2
        )

    def add_start_month_clin2(self, startMonth1):
        self.driver.find_element_by_css_selector(
            "fieldset[name='clins-1-start_date'] input[name='date-month']").send_keys(
            startMonth1
        )

    def add_start_day_clin2(self, startDay1):
        self.driver.find_element_by_css_selector(
            "fieldset[name='clins-1-start_date'] input[name='date-day']").send_keys(
            startDay1
        )

    def add_start_year_clin2(self, startYear1):
        self.driver.find_element_by_css_selector(
            "fieldset[name='clins-1-start_date'] input[name='date-year']").send_keys(
            startYear1
        )

    def add_end_month_clin2(self, endMonth1):
        self.driver.find_element_by_css_selector(
            "fieldset[name='clins-1-end_date'] input[name='date-month']").send_keys(
            endMonth1
        )

    def add_end_day_clin2(self, endDay1):
        self.driver.find_element_by_css_selector(
            "fieldset[name='clins-1-end_date'] input[name='date-day']").send_keys(endDay1)

    def add_end_year_clin2(self, endYear1):
        self.driver.find_element_by_css_selector("fieldset[name='clins-1-end_date'] input[name='date-year']").send_keys(
            endYear1
        )

    def click_next_review_TO(self):
        self.driver.find_element_by_css_selector(
            self.btn_next_review_TO_css).click()

    # Step 4 review changes and view TO summary
    # Step4 Validate header
    def validate_step4_header(self):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".sticky-cta-context"),
                "Step 4 of 5",
            )
        )

    # Step4-Validate the TaskOrder Number
    def validate_to_no_step4(self, toNumber):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".task-order__header > p"),
                toNumber,
            )
        )

    # Step4-Validate the Total Value
    def validate_step4_total_value(self, step4_total_value):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".usa-grid > .summary-item:nth-of-type(1) > .summary-item__value--large"),
                step4_total_value,
            )
        )

    # Step4-Validate the Total Obligated Value
    def validate_step4_total_ob_value(self, step4_total_ob_value):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".usa-grid > .summary-item:nth-of-type(2) > .summary-item__value--large"),
                step4_total_ob_value,
            )
        )

    # Step4-Verify the CLIN Summary details
    # Verifying the CLIN1 details
    def clin_one(self, clin1):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "table.fixed-table-wrapper > tbody > tr:nth-of-type(1) > td:nth-of-type(1)"),
                clin1,
            )
        )

    # Verifying the CLIN1- PoP
    def clin_one_pop(self, dates):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "table.fixed-table-wrapper > tbody > tr:nth-of-type(1) > td:nth-of-type(4)"),
                dates,
            )
        )

    # Verifying the CLIN1- Value
    def clin_one_value(self, clinOneValue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 "table.fixed-table-wrapper > tbody > tr:nth-of-type(1) > td.task-order__amount:nth-of-type(5)"),
                clinOneValue,
            )
        )

    # Verifying the CLIN1-Amount Obligated
    def clin_one_amount_obligated(self, clinOneAmountObligated):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 "table.fixed-table-wrapper > tbody > tr:nth-of-type(1) > td.task-order__amount:nth-of-type(6)"),
                clinOneAmountObligated,
            )
        )

    # Verifying the CLIN2 details
    def clin_two(self, clin2):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "table.fixed-table-wrapper > tbody > tr:nth-of-type(2) > td:nth-of-type(1)"),
                clin2,
            )
        )

    # Verifying the CLIN2- PoP
    def clin_two_pop(self, datesForClin2):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "table.fixed-table-wrapper > tbody > tr:nth-of-type(2) > td:nth-of-type(4)"),
                datesForClin2,
            )
        )

    # Verifying the CLIN2- Value
    def clin_two_value(self, clinTwoValue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 "table.fixed-table-wrapper > tbody > tr:nth-of-type(2) > td.task-order__amount:nth-of-type(5)"),
                clinTwoValue,
            )
        )

    # Verifying the CLIN2-Amount Obligated
    def clin_two_amount_obligated(self, clinTwoAmountObligated):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 "table.fixed-table-wrapper > tbody > tr:nth-of-type(2) > td.task-order__amount:nth-of-type(6)"),
                clinTwoAmountObligated,
            )
        )

    def click_confirm(self):
        self.driver.find_element_by_css_selector(
            self.btn_next_confirm_css).click()

    def step4_cancel_button(self):
        self.driver.find_element_by_xpath(
            "//a[contains(text(),'Cancel')]").click()

    def yes_later_btn(self):
        self.driver.find_element_by_css_selector(
            ".action-group > button[type='submit'].usa-button.usa-button-primary:nth-of-type(2)").click()

    # Step 5 agree and confirm page
    def click_checkbox_one(self):
        self.driver.find_element_by_css_selector(self.box_sign_one_css).click()

    def click_check_box_two(self):
        self.driver.find_element_by_css_selector(self.box_sign_two_css).click()

    def click_submit_TO(self):
        self.driver.find_element_by_css_selector(self.btn_submit_css).click()

    # Verifying the Success message that TO has been Successfully Uploaded
    def success_msg(self):
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "h3.usa-alert-heading"),
                "Your Task Order has been uploaded successfully.",
            )
        )

    # Click on AddNewTaskOrder Button:
    def add_new_to_button(self):
        btn = self.driver.find_element_by_xpath(
            "//a[contains(text(),'Add New Task Order')]")
        self.driver.execute_script("arguments[0].click();", btn)

    # Click on the collapse all button on the top corner
    def collapse_all(self):
        collapse = self.driver.find_element_by_css_selector(
            "a.accordion-list__collapse")
        self.driver.execute_script("arguments[0].click();", collapse)

    # Active Section
    # Click on Active TO-added javascript exector for this click to ensure it is working on IE as well
    def click_active_to(self):
        active_btn = self.driver.find_element_by_css_selector(
            self.acc_active_to_css)
        self.driver.execute_script("arguments[0].click();", active_btn)

    # Verifying the Active TO details
    def active_to(self, activeto):
        WebDriverWait(self.driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#Active h4"), activeto)
        )

    # Display message if no Active TO
    def active_blank_msg(self):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#Active > .accordion__content--empty"
                 ), "This Portfolio has no Active Task Orders.")
        )

    # Verifying the TotalValue for Active TaskOrder
    def active_to_total_value(self, activeTvalue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#Active > .accordion__content--list-item > .usa-grid > .usa-width-one-fourth:nth-of-type(2) > p",
                ), activeTvalue,
            )
        )

    # Verifying the TotalObligated Value for Active TaskOrder
    def active_to_total_obligated_value(self, activetObvalue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#Active > .accordion__content--list-item > .usa-grid > .usa-width-one-fourth:nth-of-type(3) > p",
                ), activetObvalue,
            )
        )

    # Upcoming Section:
    # Click on Upcoming TO
    def click_future_to(self):
        future_btn = self.driver.find_element_by_css_selector(
            self.acc_future_to_css)
        self.driver.execute_script("arguments[0].click();", future_btn)

    # Verifying the TO# under Upcoming section
    def upcoming_to(self, tmp):
        WebDriverWait(self.driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#Upcoming h4"), tmp)
        )

    # Verifying the TotalValue for Upcoming TaskOrder
    def upcoming_to_total_value(self, tvalue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#Upcoming > .accordion__content--list-item > .usa-grid > .usa-width-one-fourth:nth-of-type(2) > p",
                ), tvalue,
            )
        )

    # Verifying the TotalObligated value for Upcoming TaskOrder
    def upcoming_to_total_obligated_value(self, tObvalue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#Upcoming > .accordion__content--list-item > .usa-grid > .usa-width-one-fourth:nth-of-type(3) > p",
                ), tObvalue,
            )
        )

    # Display message in Upcoming section if no UpcomingTaskOrder
    def upcoming_blank_msg(self):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR, "#Upcoming > .accordion__content--empty"
                ), "This Portfolio has no Upcoming Task Orders."
            )
        )

    # Draft section
    # Click on Draft TO
    def click_draft_to(self):
        draft_btn = self.driver.find_element_by_css_selector(
            self.acc_draft_to_css)
        self.driver.execute_script("arguments[0].click();", draft_btn)

    # Display message in Draft section if no Draft TaskOrder
    def draft_blank_msg(self):
        WebDriverWait(self.driver, 15).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR, "#Draft > .accordion__content--empty"
                ), "This Portfolio has no Draft Task Orders."
            )
        )

    # Verifying the Draft section and the Task Order displays as New TaskOrder
    def draft_to(self, temp):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#Draft h4"), temp)
        )

    # Verifying the TotalValue for the Draft Task Order
    def draft_total_value(self, draftTotalValue):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#Draft > .accordion__content--list-item > .usa-grid > .usa-width-one-fourth:nth-of-type(2) > p",
                ),
                draftTotalValue,
            )
        )

    # Verifying the Total Obligated for the Draft TaskOrder
    def draft_total_obligated(self, draftTotalObligated):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#Draft > .accordion__content--list-item > .usa-grid > .usa-width-one-fourth:nth-of-type(3) > p",
                ),
                draftTotalObligated,
            )
        )

    # Expired TaskOrder Section
    # click on Expired TO
    def click_expired_to(self):
        expired_btn = self.driver.find_element_by_css_selector(
            self.acc_expired_to_css)
        self.driver.execute_script("arguments[0].click();", expired_btn)

    # Display message in Expired section if no ExpiredTaskOrder
    def expired_blank_msg(self):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR, "#Expired > .accordion__content--empty"
                ), "This Portfolio has no Expired Task Orders."
            )
        )

    # Verify the Expired TO details
    def expired_to(self, tmp):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#Expired h4"), tmp)
        )


# random Number generator for Task Order number
def random_no_generator(size=17, chars=string.digits):
    return "".join(random.choice(chars) for x in range(size))
