from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    number = StringField("Mobile Number", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password (leave blank to keep)", validators=[Optional()])
    is_admin = BooleanField("Admin")
    is_verified = BooleanField("Verified")
    is_blocked = BooleanField("Blocked")
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    number = StringField("Phone Number", validators=[Optional(), Length(max=50)])
    comment = TextAreaField("Comment", validators=[Optional()])
    category_names = StringField("Categories (comma separated, unique)", validators=[Optional()])
    brand_names = StringField("Brands (comma separated, unique)", validators=[Optional()])
    assigned_date_range_start = DateField("Assigned Date Range Start", format='%Y-%m-%d', validators=[Optional()])
    assigned_date_range_end = DateField("Assigned Date Range End", format='%Y-%m-%d', validators=[Optional()])
    subscription_date = DateField("Subscription Date", format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField("Save")

