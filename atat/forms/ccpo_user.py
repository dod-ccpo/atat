from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import Length, Required

from atat.forms.validators import Number
from atat.utils.localization import translate


class CCPOUserForm(FlaskForm):
    dod_id = StringField(
        translate("forms.new_member.dod_id_label"),
        validators=[Required(), Length(min=10, max=10), Number()],
    )
