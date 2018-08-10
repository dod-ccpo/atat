from wtforms.fields.html5 import IntegerField
from wtforms.fields import RadioField, TextAreaField, SelectField
from .fields import DateField
from .forms import ValidatedForm


class RequestForm(ValidatedForm):

    # Details of Use: General
    dod_component = SelectField(
        "DoD Component",
        description="Identify the DoD component that is requesting access to the JEDI Cloud",
        choices=[
            ("null", "Select an option"),
            ("us_air_force", "US Air Force"),
            ("us_army", "US Army"),
            ("us_navy", "US Navy"),
            ("us_marine_corps", "US Marine Corps"),
            ("joint_chiefs_of_staff", "Joint Chiefs of Staff"),
        ],
    )

    jedi_usage = TextAreaField(
        "JEDI Usage",
        description="Please tell us more about what the systems/applications you are working with and why the cloud is a good place to host these applications",
    )


    # Details of Use: Cloud Readiness
    num_software_systems = IntegerField(
        "Number of Software System",
        description="Estimate the number of software systems that will be supported by this JEDI Cloud access request",
    )

    jedi_migration = RadioField(
        description="Are you using the JEDI Cloud to migrate existing systems?",
        choices=[("yes", "Yes"), ("no", "No")],
    )

    rationalization_software_systems = RadioField(
        description="Have you completed a “rationalization” of your software systems to move to the cloud?",
        choices=[("yes", "Yes"), ("no", "No"), ("in_progress", "In Progress")],
    )

    technical_support_team = RadioField(
        description="Are you working with a technical support team experienced in cloud migrations?",
        choices=[("yes", "Yes"), ("no", "No")],
    )

    organization_providing_assistance = RadioField(  # this needs to be updated to use checkboxes instead of radio
        description="If you are receiving migration assistance, what is the type of organization providing assistance?",
        choices=[
            ("in_house_staff", "In-house staff"),
            ("contractor", "Contractor"),
            ("other_dod_organization", "Other DoD organization"),
            ("none", "None"),
        ],
    )

    engineering_assessment = RadioField(
        description="Have you completed an engineering assessment of your systems for cloud readiness?",
        choices=[("yes", "Yes"), ("no", "No"), ("in_progress", "In Progress")],
    )

    data_transfers = SelectField(
        description="How much data is being transferred to the cloud?",
        choices=[
            ("null", "Select an option"),
            ("less_than_100gb", "Less than 100GB"),
            ("100gb-500gb", "100GB-500GB"),
            ("500gb-1tb", "500GB-1TB"),
            ("1tb-50tb", "1TB-50TB"),
            ("50tb-100tb", "50TB-100TB"),
            ("100tb-500tb", "100TB-500TB"),
            ("500tb-1pb", "500TB-1PB"),
            ("1pb-5pb", "1PB-5PB"),
            ("5pb-10pb", "5PB-10PB"),
            ("above_10pb", "Above 10PB"),
        ],
    )

    expected_completion_date = SelectField(
        description="When do you expect to complete your migration to the JEDI Cloud?",
        choices=[
            ("null", "Select an option"),
            ("less_than_1_month", "Less than 1 month"),
            ("1_to_3_months", "1-3 months"),
            ("3_to_6_months", "3-6 months"),
            ("above_12_months", "Above 12 months"),
        ],
    )

    cloud_native = RadioField(
        "Are your software systems being developed cloud native?",
        choices=[("yes", "Yes"), ("no", "No")],
    )

    # Details of Use: Financial Usage
    estimated_monthly_spend = IntegerField(
        "Estimated monthly spend",
        description='Use the <a href="#" target="_blank" class="icon-link">JEDI CSP Calculator</a> to estimate your monthly cloud resource usage and enter the dollar amount below. Note these estimates are for initial approval only. After the request is approved, you will be asked to provide a valid Task Order number with specific CLIN amounts for cloud services.',
    )

    dollar_value = IntegerField(
        "Total Spend",
        description="What is your total expected budget for this JEDI Cloud Request?",
    )

    number_user_sessions = IntegerField(
        description="How many user sessions do you expect on these systems each day?"
    )

    average_daily_traffic = IntegerField(
        "Average Daily Traffic (Number of Requests)",
        description="What is the average daily traffic you expect the systems under this cloud contract to use?"
    )

    average_daily_traffic_gb = IntegerField(
        "Average Daily Traffic (GB)",
        description="What is the average daily traffic you expect the systems under this cloud contract to use?"
    )

    start_date = DateField(
        description="When do you expect to start using the JEDI Cloud (not for billing purposes)?"
    )
