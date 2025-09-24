from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class BrandForm(FlaskForm):
    id = HiddenField()
    code = StringField("Code", validators=[DataRequired(), Length(max=255)])
    product_count = IntegerField("Product Count")
    name = StringField("Brand Name", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Save")
