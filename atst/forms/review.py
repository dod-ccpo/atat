from wtforms.fields import BooleanField
from wtforms_tornado import Form


class ReviewForm(Form):
    reviewed = BooleanField("I have reviewed this data and it is correct.")
