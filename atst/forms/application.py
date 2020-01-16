from .forms import BaseForm, remove_empty_string
from wtforms.fields import StringField, TextAreaField, FieldList
from wtforms.validators import Required, Optional, Length
from atst.forms.validators import ListItemRequired, ListItemsUnique, Name, AlphaNumeric
from atst.utils.localization import translate


class EditEnvironmentForm(BaseForm):
    name = StringField(
        label=translate("forms.environments.name_label"),
        validators=[Required(), Name(), Length(max=100)],
        filters=[remove_empty_string],
    )


class NameAndDescriptionForm(BaseForm):
    name = StringField(
        label=translate("forms.application.name_label"),
        validators=[Required(), Name(), Length(max=100)],
        filters=[remove_empty_string],
    )
    description = TextAreaField(
        label=translate("forms.application.description_label"),
        validators=[Optional()],
        filters=[remove_empty_string],
    )


class EnvironmentsForm(BaseForm):
    environment_names = FieldList(
        StringField(
            label=translate("forms.application.environment_names_label"),
            filters=[remove_empty_string],
            validators=[AlphaNumeric(), Length(max=100)],
        ),
        validators=[
            ListItemRequired(
                message=translate(
                    "forms.application.environment_names_required_validation_message"
                )
            ),
            ListItemsUnique(
                message=translate(
                    "forms.application.environment_names_unique_validation_message"
                )
            ),
        ],
    )
