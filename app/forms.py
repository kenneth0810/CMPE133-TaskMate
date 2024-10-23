from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()])
    description = StringField('Task Description', default=None)
    priority = SelectField('Priority', choices=[
        ('', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default=None)
    due_date = DateField('Due Date', format='%m-%d-%Y', default=None)
    due_time = TimeField('Due Time', format='%I:%M %p', default=None)
    is_completed = BooleanField('Complete Task', default=False)
    submit = SubmitField('Create Task')