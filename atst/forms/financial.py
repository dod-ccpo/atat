from wtforms.fields.html5 import IntegerField, EmailField, TelField
from wtforms.fields import (
    RadioField,
    StringField,
    SelectField,
    FormField,
    TextAreaField,
    BooleanField,
)
from wtforms.validators import Required, ValidationError
from wtforms_tornado import Form
from .date import DateForm

class FinancialForm(Form):
    # Financial Verification

    task_order_id = StringField(
        "Task Order Number associated with this request.", validators=[Required()]
    )

    fname_co = StringField("Contracting Officer First Name", validators=[Required()])
    lname_co = StringField("Contracting Officer Last Name", validators=[Required()])

    email_co = StringField("Contracting Officer Email", validators=[Required()])

    office_co = StringField("Contracting Office Office", validators=[Required()])

    fname_cor = StringField(
        "Contracting Officer Representative (COR) First Name", validators=[Required()]
    )

    lname_cor = StringField(
        "Contracting Officer Representative (COR) Last Name", validators=[Required()]
    )

    email_cor = StringField(
        "Contracting Officer Representative (COR) Email", validators=[Required()]
    )

    office_cor = StringField(
        "Contracting Officer Representative (COR) Office", validators=[Required()]
    )


    funding_type = SelectField(
        validators=[Required()],
        choices=[
            ("", "- Select -"),
            ("RDTE","Research, Development, Testing & Evaluation (RDT&E)"),
            ("OM","Operations & Maintenance (O&M)"),
            ("PROC","Procurement (PROC)"),
            ("OTHER","Other"),
        ],
    )


    funding_type_other = StringField(
        "If other, please specify", validators=[Required()]
    )

    clin_0001 = StringField(
        "CLIN 0001 - Unclassified IaaS and PaaS Amount", validators=[Required()]
    )

    clin_0003 = StringField(
        "CLIN 0003 - Unclassified Cloud Support Package", validators=[Required()]
    )

    clin_1001 = StringField(
        "CLIN 1001 - Unclassified IaaS and PaaS Amount OPTION PERIOD 1",
        validators=[Required()],
    )

    clin_1003 = StringField(
        "CLIN 1003 - Unclassified Cloud Support Package OPTION PERIOD 1",
        validators=[Required()],
    )

    clin_2001 = StringField(
        "CLIN 2001 - Unclassified IaaS and PaaS Amount OPTION PERIOD 2",
        validators=[Required()],
    )

    clin_2003 = StringField(
        "CLIN 2003 - Unclassified Cloud Support Package OPTION PERIOD 2",
        validators=[Required()],
    )
