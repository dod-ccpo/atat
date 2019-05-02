from .forms import BaseForm
from wtforms.fields import StringField, TextAreaField, FieldList, HiddenField
from wtforms.validators import Required
from atst.forms.validators import ListItemRequired, ListItemsUnique
from atst.utils.localization import translate


class EditEnvironmentForm(BaseForm):
    id = HiddenField()
    name = StringField(
        label=translate("forms.environments.name_label"), validators=[Required()]
    )


class ApplicationForm(BaseForm):
    name = StringField(
        label=translate("forms.application.name_label"), validators=[Required()]
    )
    description = TextAreaField(
        label=translate("forms.application.description_label"), validators=[Required()]
    )


class NewApplicationForm(ApplicationForm):
    environment_names = FieldList(
        StringField(label=translate("forms.application.environment_names_label")),
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
