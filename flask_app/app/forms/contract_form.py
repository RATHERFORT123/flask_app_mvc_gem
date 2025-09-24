from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, DateField
from wtforms.validators import DataRequired, Optional
from wtforms import SubmitField

# class ContractForm(FlaskForm):
    # ... existing fields ...

class ContractForm(FlaskForm):
    submit = SubmitField('Submit')
    contract_id = StringField('Contract ID', validators=[DataRequired()])
    organization_type = StringField('Organization Type', validators=[Optional()])
    ministry = StringField('Ministry', validators=[Optional()])
    department = StringField('Department', validators=[Optional()])
    organization_name = StringField('Organization Name', validators=[Optional()])
    office_zone = StringField('Office Zone', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    buyer_designation = StringField('Buyer Designation', validators=[Optional()])
    buying_mode = StringField('Buying Mode', validators=[Optional()])
    bid_number = StringField('Bid Number', validators=[Optional()])
    contract_date = DateField('Contract Date', format='%Y-%m-%d', validators=[Optional()])
    total = FloatField('Total', validators=[Optional()])

    # Item fields
    service = StringField('Service', validators=[Optional()])
    category_name = StringField('Category Name', validators=[Optional()])
    product = StringField('Product', validators=[Optional()])
    brand = StringField('Brand', validators=[Optional()])
    model = StringField('Model', validators=[Optional()])
    hsn_code = StringField('HSN Code', validators=[Optional()])
    ordered_quantity = FloatField('Ordered Quantity', validators=[Optional()])
    price = FloatField('Price', validators=[Optional()])
