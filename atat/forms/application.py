from wtforms.fields import FieldList, StringField, TextAreaField
from wtforms.validators import Length, Optional, Required

from atat.forms.validators import AlphaNumeric, ListItemRequired, ListItemsUnique, Name
from atat.utils.localization import translate

from .forms import BaseForm, remove_empty_string


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
        validators=[Optional(), Length(max=1_000)],
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
