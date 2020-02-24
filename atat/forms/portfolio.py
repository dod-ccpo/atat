from wtforms.fields import (
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.validators import Length, InputRequired
from atat.forms.validators import Name
from wtforms.widgets import ListWidget, CheckboxInput

from .forms import BaseForm
from atat.utils.localization import translate

from .data import SERVICE_BRANCHES


class PortfolioForm(BaseForm):
    name = StringField(
        translate("forms.portfolio.name.label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name.length_validation_message"),
            ),
            Name(),
        ],
    )
    description = TextAreaField(
        translate("forms.portfolio.description.label"), validators=[Length(max=1_000)]
    )


class PortfolioCreationForm(PortfolioForm):
    defense_component = SelectMultipleField(
        translate("forms.portfolio.defense_component.title"),
        description=translate("forms.portfolio.defense_component.help_text"),
        choices=SERVICE_BRANCHES,
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        validators=[
            InputRequired(
                message=translate(
                    "forms.portfolio.defense_component.validation_message"
                )
            )
        ],
    )
