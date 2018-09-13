from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length

from atst.forms.validators import IsNumber
from atst.forms.fields import SelectField

from .data import WORKSPACE_ROLES


class NewMemberForm(Form):

    first_name = StringField(label="First Name", validators=[Required()])
    last_name = StringField(label="Last Name", validators=[Required()])
    email = EmailField("Email Address", validators=[Required(), Email()])
    dod_id = StringField("DOD ID", validators=[Required(), Length(min=10), IsNumber()])
    workspace_role = SelectField(
        "Workspace Role", choices=WORKSPACE_ROLES, validators=[Required()], default="",
        description="The workspace role controls whether a member is permitted to organize a workspace into projects and environments, add members to this workspace, and view billing information."
    )
