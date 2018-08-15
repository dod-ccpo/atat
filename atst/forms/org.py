from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import RadioField, StringField, SelectField
from wtforms.validators import Required, Email
import pendulum
from .fields import DateField
from .forms import ValidatedForm
from .validators import DateRange, PhoneNumber, Alphabet


class OrgForm(ValidatedForm):
    fname_request = StringField("First Name", validators=[Required(), Alphabet()])

    lname_request = StringField("Last Name", validators=[Required(), Alphabet()])

    email_request = EmailField("E-mail Address", validators=[Required(), Email()])

    phone_number = TelField("Phone Number",
        description='Enter a 10-digit phone number',
        validators=[Required(), PhoneNumber()])

    service_branch = SelectField(
        "Service Branch or Agency",
        description="Which services and organizations do you belong to within the DoD?",
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
            ("Uniform Services University of the Health Sciences", "Uniform Services University of the Health Sciences"),
            ("US Cyber Command (USCYBERCOM)", "US Cyber Command (USCYBERCOM)"),
            ("US Special Operations Command (USSOCOM)", "US Special Operations Command (USSOCOM)"),
            ("US Strategic Command (USSTRATCOM)", "US Strategic Command (USSTRATCOM)"),
            ("US Transportation Command (USTRANSCOM)", "US Transportation Command (USTRANSCOM)"),
            ("Washington Headquarters Services", "Washington Headquarters Services"),
        ],
    )

    citizenship = RadioField(
        description="What is your citizenship status?",
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ],
        validators=[Required()],
    )

    designation = RadioField(
        "Designation of Person",
        description="What is your designation within the DoD?",
        choices=[
            ("military", "Military"),
            ("civilian", "Civilian"),
            ("contractor", "Contractor"),
        ],
        validators=[Required()],
    )

    date_latest_training = DateField(
        "Latest Information Assurance (IA) Training completion date",
        description="To complete the training, you can find it in <a class=\"icon-link\" href=\"https://iatraining.disa.mil/eta/disa_cac2018/launchPage.htm\" target=\"_blank\">Information Assurance Cyber Awareness Challange</a> website.",
        validators=[
            Required(),
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            ),
        ],
    )
