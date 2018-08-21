import re
from wtforms.fields.html5 import EmailField
from wtforms.fields import StringField
from wtforms.validators import Required, Email, Regexp

from atst.domain.exceptions import NotFoundError
from atst.domain.pe_numbers import PENumbers
from atst.domain.task_orders import TaskOrders

from .fields import NewlineListField, SelectField
from .forms import ValidatedForm


PE_REGEX = re.compile(
    r"""
    (0?\d) # program identifier
    (0?\d) # category
    (\d)   # activity
    (\d+)  # sponsor element
    (.+)   # service
""",
    re.X,
)

TREASURY_CODE_REGEX = re.compile(r"^0*([1-9]{4}|[1-9]{6})$")

BA_CODE_REGEX = re.compile(r"^0*[1-9]{2}\w?$")

def suggest_pe_id(pe_id):
    suggestion = pe_id
    match = PE_REGEX.match(pe_id)
    if match:
        (program, category, activity, sponsor, service) = match.groups()
        if len(program) < 2:
            program = "0" + program
        if len(category) < 2:
            category = "0" + category
        suggestion = "".join((program, category, activity, sponsor, service))

    if suggestion != pe_id:
        return suggestion
    return None


def validate_pe_id(field, existing_request):
    try:
        PENumbers.get(field.data)
    except NotFoundError:
        suggestion = suggest_pe_id(field.data)
        error_str = (
            "We couldn't find that PE number. {}"
            "If you have double checked it you can submit anyway. "
            "Your request will need to go through a manual review."
        ).format('Did you mean "{}"? '.format(suggestion) if suggestion else "")
        field.errors += (error_str,)
        return False

    return True


def validate_task_order_number(field):
    try:
        TaskOrders.get(field.data)
    except NotFoundError:
        field.errors += ("Task Order number not found",)
        return False

    return True


class BaseFinancialForm(ValidatedForm):
    def reset(self):
        """
        Reset UII info so that it can be de-parsed rendered properly.
        This is a stupid workaround, and there's probably a better way.
        """
        self.uii_ids.process_data(self.uii_ids.data)

    def perform_extra_validation(self, existing_request):
        valid = True
        if not existing_request or existing_request.get("pe_id") != self.pe_id.data:
            valid = validate_pe_id(self.pe_id, existing_request)
        return valid

    @property
    def is_missing_task_order_number(self):
        return False

    task_order_number = StringField(
        "Task Order Number associated with this request",
        description="Include the original Task Order number (including the 000X at the end). Do not include any modification numbers. Note that there may be a lag between approving a task order and when it becomes available in our system.",
        validators=[Required()]
    )

    uii_ids = NewlineListField(
        "Unique Item Identifier (UII)s related to your application(s) if you already have them",
        validators=[Required()]
    )

    pe_id = StringField("Program Element (PE) Number related to your request", validators=[Required()])

    treasury_code = StringField("Program Treasury Code", validators=[Required(), Regexp(TREASURY_CODE_REGEX)])

    ba_code = StringField("Program Budget Activity (BA) Code", validators=[Required(), Regexp(BA_CODE_REGEX)])

    fname_co = StringField("Contracting Officer First Name", validators=[Required()])
    lname_co = StringField("Contracting Officer Last Name", validators=[Required()])

    email_co = EmailField("Contracting Officer Email", validators=[Required(), Email()])

    office_co = StringField("Contracting Officer Office", validators=[Required()])

    fname_cor = StringField(
        "Contracting Officer Representative (COR) First Name", validators=[Required()]
    )

    lname_cor = StringField(
        "Contracting Officer Representative (COR) Last Name", validators=[Required()]
    )

    email_cor = EmailField(
        "Contracting Officer Representative (COR) Email",
        validators=[Required(), Email()],
    )

    office_cor = StringField(
        "Contracting Officer Representative (COR) Office", validators=[Required()]
    )


class FinancialForm(BaseFinancialForm):
    def perform_extra_validation(self, existing_request):
        previous_valid = super().perform_extra_validation(existing_request)
        task_order_valid = validate_task_order_number(self.task_order_number)
        return previous_valid and task_order_valid

    @property
    def is_missing_task_order_number(self):
        return "task_order_number" in self.errors


class ExtendedFinancialForm(BaseFinancialForm):
    def validate(self, *args, **kwargs):
        if self.funding_type.data == "OTHER":
            self.funding_type_other.validators.append(Required())
        return super().validate(*args, **kwargs)

    funding_type = SelectField(
        description="What is the source of funding?",
        choices=[
            ("", "- Select -"),
            ("RDTE", "Research, Development, Testing & Evaluation (RDT&E)"),
            ("OM", "Operations & Maintenance (O&M)"),
            ("PROC", "Procurement (PROC)"),
            ("OTHER", "Other"),
        ],
        validators=[Required()],
        render_kw={"required": False}
    )

    funding_type_other = StringField("If other, please specify")

    clin_0001 = StringField(
        "<dl><dt>CLIN 0001</dt> - <dd>Unclassified IaaS and PaaS Amount</dd></dl>",
        validators=[Required()],
        description="Review your task order document, the amounts for each CLIN must match exactly here"
    )

    clin_0003 = StringField(
        "<dl><dt>CLIN 0003</dt> - <dd>Unclassified Cloud Support Package</dd></dl>",
        validators=[Required()],
        description="Review your task order document, the amounts for each CLIN must match exactly here"
    )

    clin_1001 = StringField(
        "<dl><dt>CLIN 1001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 1</dd></dl>",
        validators=[Required()],
        description="Review your task order document, the amounts for each CLIN must match exactly here"
    )

    clin_1003 = StringField(
        "<dl><dt>CLIN 1003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 1</dd></dl>",
        validators=[Required()],
        description="Review your task order document, the amounts for each CLIN must match exactly here"
    )

    clin_2001 = StringField(
        "<dl><dt>CLIN 2001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 2</dd></dl>",
        validators=[Required()],
        description="Review your task order document, the amounts for each CLIN must match exactly here"
    )

    clin_2003 = StringField(
        "<dl><dt>CLIN 2003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 2</dd></dl>",
        validators=[Required()],
        description="Review your task order document, the amounts for each CLIN must match exactly here"
    )
