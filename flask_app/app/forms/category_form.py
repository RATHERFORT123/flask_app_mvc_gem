from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class CategoryForm(FlaskForm):
    id = HiddenField()
    value = StringField("Value", validators=[DataRequired(), Length(max=255)])
    text = StringField("Text", validators=[DataRequired()])
    submit = SubmitField("Save")
