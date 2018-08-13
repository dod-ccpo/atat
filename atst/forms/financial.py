import re
from wtforms.fields.html5 import EmailField
from wtforms.fields import StringField, SelectField
from wtforms.validators import Required, Email

from atst.domain.exceptions import NotFoundError
from atst.domain.pe_numbers import PENumbers

from .fields import NewlineListField
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


class FinancialForm(ValidatedForm):
    def perform_extra_validation(self, existing_request):
        valid = True
        if not existing_request or existing_request.get("pe_id") != self.pe_id.data:
            valid = validate_pe_id(self.pe_id, existing_request)
        return valid

    task_order_id = StringField(
        "Task Order Number associated with this request",
        description="Include the original Task Order number (including the 000X at the end); this field is not requesting any modification numbers.",
        validators=[Required()]
    )

    uii_ids = NewlineListField(
        "Unique Item Identifier (UII)s related to your application(s) if you already have them",
        description="consult a finance or contracting expert in your office to help identify which applications have a UII number and where they are located."
    )

    pe_id = StringField("Program Element (PE) Number related to your request",
        validators=[Required()]
    )

    treasury_code = StringField("Program Treasury Code")

    ba_code = StringField("Program BA Code")

    fname_co = StringField("Contracting Officer First Name",
        validators=[Required()]
    )
    lname_co = StringField("Contracting Officer Last Name",
        validators=[Required()]
    )

    email_co = EmailField("Contracting Officer Email",
        validators=[Required(), Email()]
    )

    office_co = StringField("Contracting Office Office",
        validators=[Required()]
    )

    fname_cor = StringField(
        "Contracting Officer Representative (COR) First Name",
        validators=[Required()]
    )

    lname_cor = StringField(
        "Contracting Officer Representative (COR) Last Name",
        validators=[Required()]
    )

    email_cor = EmailField(
        "Contracting Officer Representative (COR) Email",
        validators=[Required(), Email()],
    )

    office_cor = StringField(
        "Contracting Officer Representative (COR) Office",
        validators=[Required()]
    )

    funding_type = SelectField(
        validators=[Required()],
        choices=[
            ("", "- Select -"),
            ("RDTE", "Research, Development, Testing & Evaluation (RDT&E)"),
            ("OM", "Operations & Maintenance (O&M)"),
            ("PROC", "Procurement (PROC)"),
            ("OTHER", "Other"),
        ],
    )

    funding_type_other = StringField(
        "If other, please specify",
        validators=[Required()]
    )

    clin_0001 = StringField(
        "<dl><dt>CLIN 0001</dt> - <dd>Unclassified IaaS and PaaS Amount</dd></dl>",
        validators=[Required()],
    )

    clin_0003 = StringField(
        "<dl><dt>CLIN 0003</dt> - <dd>Unclassified Cloud Support Package</dd></dl>",
        validators=[Required()],
    )

    clin_1001 = StringField(
        "<dl><dt>CLIN 1001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 1</dd></dl>",
        validators=[Required()],
    )

    clin_1003 = StringField(
        "<dl><dt>CLIN 1003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 1</dd></dl>",
        validators=[Required()],
    )

    clin_2001 = StringField(
        "<dl><dt>CLIN 2001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 2</dd></dl>",
        validators=[Required()],
    )

    clin_2003 = StringField(
        "<dl><dt>CLIN 2003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 2</dd></dl>",
        validators=[Required()],
    )

    to_upload = StringField(
        "Upload a copy of your Task Order",
        validators=[Required()],
    )
