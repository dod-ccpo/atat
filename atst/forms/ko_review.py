from flask_wtf.file import FileAllowed

from wtforms.fields import StringField, TextAreaField, FileField
from wtforms.validators import Optional, Length, InputRequired

from .forms import CacheableForm
from .validators import IsNumber

from atst.utils.localization import translate


class KOReviewForm(CacheableForm):
    pdf = FileField(
        translate("forms.ko_review.pdf_label"),
        description=translate("forms.ko_review.pdf_description"),
        validators=[
            FileAllowed(
                ["pdf", "png"], translate("forms.task_order.file_format_not_allowed")
            ),
            InputRequired(),
        ],
        render_kw={"required": False, "accept": ".pdf,.png,application/pdf,image/png"},
    )
    to_number = StringField(
        translate("forms.ko_review.to_number"), validators=[Length(min=10), IsNumber()]
    )
    loa = StringField(
        translate("forms.ko_review.loa"), validators=[Length(min=10), IsNumber()]
    )
    custom_clauses = TextAreaField(
        translate("forms.ko_review.custom_clauses_label"),
        description=translate("forms.ko_review.custom_clauses_description"),
        validators=[Optional()],
    )
