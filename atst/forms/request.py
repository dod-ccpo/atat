from wtforms.fields.html5 import IntegerField
from wtforms.fields import RadioField, TextAreaField, SelectField
from wtforms.validators import Optional, Required

from .fields import DateField
from .forms import ValidatedForm
from atst.domain.requests import Requests


class RequestForm(ValidatedForm):

    def validate(self, *args, **kwargs):
        if self.jedi_migration.data == 'no':
            self.rationalization_software_systems.validators.append(Optional())
            self.technical_support_team.validators.append(Optional())
            self.organization_providing_assistance.validators.append(Optional())
            self.engineering_assessment.validators.append(Optional())
            self.data_transfers.validators.append(Optional())
            self.expected_completion_date.validators.append(Optional())
        elif self.jedi_migration.data == 'yes':
            if self.technical_support_team.data == 'no':
                self.organization_providing_assistance.validators.append(Optional())
            self.cloud_native.validators.append(Optional())

        try:
            annual_spend = int(self.estimated_monthly_spend.data or 0) * 12
        except ValueError:
            annual_spend = 0

        if annual_spend > Requests.AUTO_APPROVE_THRESHOLD:
            self.number_user_sessions.validators.append(Required())
            self.average_daily_traffic.validators.append(Required())

        return super(RequestForm, self).validate(*args, **kwargs)

    # Details of Use: General
    dod_component = SelectField(
        "DoD Component",
        description="Identify the DoD component that is requesting access to the JEDI Cloud",
        choices=[
            ("null", "Select an option"),
            ("Air Force, Department of the", "Air Force, Department of the"),
            ("Army and Air Force Exchange Service", "Army and Air Force Exchange Service"),
            ("Army, Department of the", "Army, Department of the"),
            ("Defense Advanced Research Projects Agency", "Defense Advanced Research Projects Agency"),
            ("Defense Commissary Agency", "Defense Commissary Agency"),
            ("Defense Contract Audit Agency", "Defense Contract Audit Agency"),
            ("Defense Contract Management Agency", "Defense Contract Management Agency"),
            ("Defense Finance & Accounting Service", "Defense Finance & Accounting Service"),
            ("Defense Health Agency", "Defense Health Agency"),
            ("Defense Information System Agency", "Defense Information System Agency"),
            ("Defense Intelligence Agency", "Defense Intelligence Agency"),
            ("Defense Legal Services Agency", "Defense Legal Services Agency"),
            ("Defense Logistics Agency", "Defense Logistics Agency"),
            ("Defense Media Activity", "Defense Media Activity"),
            ("Defense Micro Electronics Activity", "Defense Micro Electronics Activity"),
            ("Defense POW-MIA Accounting Agency", "Defense POW-MIA Accounting Agency"),
            ("Defense Security Cooperation Agency", "Defense Security Cooperation Agency"),
            ("Defense Security Service", "Defense Security Service"),
            ("Defense Technical Information Center", "Defense Technical Information Center"),
            ("Defense Technology Security Administration", "Defense Technology Security Administration"),
            ("Defense Threat Reduction Agency", "Defense Threat Reduction Agency"),
            ("DoD Education Activity", "DoD Education Activity"),
            ("DoD Human Recourses Activity", "DoD Human Recourses Activity"),
            ("DoD Inspector General", "DoD Inspector General"),
            ("DoD Test Resource Management Center", "DoD Test Resource Management Center"),
            ("Headquarters Defense Human Resource Activity ", "Headquarters Defense Human Resource Activity "),
            ("Joint Staff", "Joint Staff"),
            ("Missile Defense Agency", "Missile Defense Agency"),
            ("National Defense University", "National Defense University"),
            ("National Geospatial Intelligence Agency", "National Geospatial Intelligence Agency"),
            ("National Geospatial Intelligence Agency (NGA)", "National Geospatial Intelligence Agency (NGA)"),
            ("National Oceanic and Atmospheric Administration (NOAA)", "National Oceanic and Atmospheric Administration (NOAA)"),
            ("National Reconnaissance Office", "National Reconnaissance Office"),
            ("National Reconnaissance Office (NRO)", "National Reconnaissance Office (NRO)"),
            ("National Security Agency (NSA)", "National Security Agency (NSA)"),
            ("National Security Agency-Central Security Service", "National Security Agency-Central Security Service"),
            ("Navy, Department of the", "Navy, Department of the"),
            ("Office of Economic Adjustment", "Office of Economic Adjustment"),
            ("Office of the Secretary of Defense", "Office of the Secretary of Defense"),
            ("Pentagon Force Protection Agency", "Pentagon Force Protection Agency"),
            ("TRANSCOM", "TRANSCOM"),
            ("Uniform Services University of the Health Sciences", "Uniform Services University of the Health Sciences"),
            ("US Cyber Command (USCYBERCOM)", "US Cyber Command (USCYBERCOM)"),
            ("US Special Operations Command (USSOCOM)", "US Special Operations Command (USSOCOM)"),
            ("US Strategic Command (USSTRATCOM)", "US Strategic Command (USSTRATCOM)"),
            ("US Transportation Command (USTRANSCOM)", "US Transportation Command (USTRANSCOM)"),
            ("Washington Headquarters Services", "Washington Headquarters Services"),
        ],
    )

    jedi_usage = TextAreaField(
        "JEDI Usage",
        description="Your answer will help us provide tangible examples to DoD leadership how and why commercial cloud resources are accelerating the Department's missions",
    )


    # Details of Use: Cloud Readiness
    num_software_systems = IntegerField(
        "Number of Software System",
        description="Estimate the number of software systems that will be supported by this JEDI Cloud access request",
    )

    jedi_migration = RadioField(
        "JEDI Migration",
        description="Are you using the JEDI Cloud to migrate existing systems?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    rationalization_software_systems = RadioField(
        description="Have you completed a “rationalization” of your software systems to move to the cloud?",
        choices=[("yes", "Yes"), ("no", "No"), ("in_progress", "In Progress")],
        default="",
    )

    technical_support_team = RadioField(
        description="Are you working with a technical support team experienced in cloud migrations?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    organization_providing_assistance = RadioField(  # this needs to be updated to use checkboxes instead of radio
        description="If you are receiving migration assistance, what is the type of organization providing assistance?",
        choices=[
            ("in_house_staff", "In-house staff"),
            ("contractor", "Contractor"),
            ("other_dod_organization", "Other DoD organization"),
            ("none", "None"),
        ],
        default="",
    )

    engineering_assessment = RadioField(
        description="Have you completed an engineering assessment of your systems for cloud readiness?",
        choices=[("yes", "Yes"), ("no", "No"), ("in_progress", "In Progress")],
        default="",
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
        description="Are your software systems being developed cloud native?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    # Details of Use: Financial Usage
    estimated_monthly_spend = IntegerField(
        "Estimated monthly spend",
        description='Use the <a href="#" target="_blank" class="icon-link">JEDI CSP Calculator</a> to estimate your <b>monthly</b> cloud resource usage and enter the dollar amount below. Note these estimates are for initial approval only. After the request is approved, you will be asked to provide a valid Task Order number with specific CLIN amounts for cloud services.',
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
