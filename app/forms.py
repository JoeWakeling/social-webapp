from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


class SignupForm(FlaskForm):
    display_name = StringField('Display name', validators=[DataRequired(), Length(min=3, max=16)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=16)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=32)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password'), Length(min=10, max=32)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=32)])
    submit = SubmitField('Sign in')


class NewPostForm(FlaskForm):
    body = TextAreaField('Enter post', validators=[DataRequired(), Length(max=1024)])
    submit = SubmitField('Sign in')


class ChangeDisplayNameForm(FlaskForm):
    display_name = StringField('New display name', validators=[DataRequired(), Length(min=3, max=16)])
    submit = SubmitField('Update')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired(), Length(max=32)])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(max=32)])
    submit = SubmitField('Update')
