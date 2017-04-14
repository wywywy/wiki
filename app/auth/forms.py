from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from ..models import User


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(8, 16)])
    password2 = PasswordField('confirm_password',
                                    validators=[DataRequired(), EqualTo('password',
                                                                         message='password should be match.')])
    submit = SubmitField('Submit')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in use.')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(8,16)])
    submit = SubmitField('Submit')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is not registered.')


class PasswordResetForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    new_password = PasswordField('new_password', validators=[DataRequired(), Length(8, 16)])
    confirm_password = PasswordField('confirm_password', validators=[EqualTo('new_password')])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is not registered.')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    new_password = PasswordField('new_password', validators=[DataRequired(), Length(8, 16)])
    confirm_password = PasswordField('confirm_password', validators=[EqualTo('new_password')])
    submit = SubmitField('Submit')


class ChangeEmailRequestForm(FlaskForm):
    new_email = StringField('new_email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ChangeEmailForm(FlaskForm):
    old_email = StringField('old_email', validators=[DataRequired(), Email()])
    new_email = StringField('new_email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Old email is not in use.')



