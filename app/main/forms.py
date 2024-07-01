from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length, Regexp

from app.utils.forms import HasTimezoneSelectForm


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class ResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email address of your account',
        validators=[InputRequired()],
    )
    submit = SubmitField('Submit')


class NewPasswordForm(FlaskForm):
    password = PasswordField(
        'Type your new password',
        validators=[InputRequired(), Length(min=8)]
    )
    confirm_password = PasswordField(
        'Confirm your password',
        validators=[EqualTo('password')]
    )
    submit = SubmitField('Submit')


class RegisterForm(HasTimezoneSelectForm):
    email = EmailField('Email', validators=[InputRequired()])
    company_name = StringField(
        'Company name',
        validators=[
            InputRequired(),
            Length(min=3, max=20),
            Regexp(r'^\w[\w.\-_ ]+\w$', message='Symbols allowed . _ -'),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=8)],
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[InputRequired(), EqualTo('password')],
    )
    submit = SubmitField('Register')
