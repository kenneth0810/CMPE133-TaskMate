from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError, Optional
from .models import User

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    # Custom validation method for email uniqueness:
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class PasswordResetInAccountForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()])
    description = TextAreaField('Task Description', default=None)
    priority = SelectField('Priority', choices=[
        ('', 'None'),
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High')
    ], default=None)
    due_date = DateField('Due Date', default=None, validators=[Optional()])
    due_time = TimeField('Due Time', default=None, validators=[Optional()])
    is_completed = BooleanField('Complete Task', default=False)
    submit = SubmitField('Create Task')