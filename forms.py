from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


us_states = ["al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
             "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"]


class CitySearchForm(FlaskForm):
    city = StringField("City", validators=[
                       DataRequired(message=("Please enter city."))])
    state = SelectField("State", choices=[(state, state) for state in us_states], validators=[
                        DataRequired(message=("Please enter state."))])
