from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import Required, Email, Length, Optional
from wtforms.fields import StringField

from atat.forms.validators import Number, PhoneNumber, Name
from atat.utils.localization import translate


class NewForm(FlaskForm):
    first_name = StringField(
        label=translate("forms.new_member.first_name_label"),
        validators=[Required(), Name(), Length(max=100)],
    )
    last_name = StringField(
        label=translate("forms.new_member.last_name_label"),
        validators=[Required(), Name(), Length(max=100)],
    )
    email = EmailField(
        translate("forms.new_member.email_label"), validators=[Required(), Email()]
    )
    phone_number = TelField(
        translate("forms.new_member.phone_number_label"),
        validators=[Optional(), PhoneNumber()],
    )
    phone_ext = StringField("Extension", validators=[Number(), Length(max=10)])
    dod_id = StringField(
        translate("forms.new_member.dod_id_label"),
        validators=[Required(), Length(min=10), Number()],
    )
