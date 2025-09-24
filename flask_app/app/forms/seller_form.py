from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Email

class SellerForm(FlaskForm):
    contract_no = StringField('Contract No', validators=[DataRequired()])
    generated_date = DateField('Generated Date', format='%Y-%m-%d', validators=[Optional()])
    category_name = StringField('Category Name', validators=[Optional()])
    seller_id = StringField('Seller ID', validators=[Optional()])
    company_name = StringField('Company Name', validators=[Optional()])
    contact_no = StringField('Contact No.', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Address', validators=[Optional()])
    msme_reg_no = StringField('MSME Reg. No', validators=[Optional()])
    gstin = StringField('GSTIN', validators=[Optional()])
    submit = SubmitField('Submit')
