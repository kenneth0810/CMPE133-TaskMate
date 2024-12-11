from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from wtforms.widgets import TextArea
from .models import User

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()]) # field must be email
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()]) # field must be email
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=32)]) # field must be between 8 and 32 characters
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')]) # field must match password field
    submit = SubmitField('Register')

    # Custom validation method for email uniqueness:
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() # checks if a user exists under the specified email
        if user is not None:
            raise ValidationError('Please use a different email address.') # if there is a user under the email, raise an error

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()]) # field is required for adding any task to the db
    description = TextAreaField('Task Description', default=None)
    priority = SelectField('Priority', choices=[
        ('', 'None'),
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High')
    ], default=None) # There are four priorities of None, Low, Medium, and High
    due_date = DateField('Due Date', default=None, validators=[Optional()]) # field is optional
    due_time = TimeField('Due Time', default=None, validators=[Optional()]) # field is optional
    is_completed = BooleanField('Complete Task', default=False) # keeps track of if the field is completed or not
    submit = SubmitField('Create Task')

class PasswordForm(FlaskForm):
    old_password = PasswordField("", 
                                 validators = [DataRequired()], 
                                 render_kw ={"placeholder":"Enter Original Password"})
    new_password = PasswordField("", 
                                 validators=[DataRequired(), Length(min=8, max=32)], 
                                 render_kw={"placeholder": "Enter a New Password"}) # field must be between 8 and 32 characters
    confirm = PasswordField("", 
                            validators=[DataRequired()], 
                            render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField("Update")

    def validate_old_password(self, form): 
        if not check_password_hash(current_user.password, form.data):
            raise ValidationError('Incorrect Original Password!') # compare hash of the submitted password to the hash in the db to ensure that they match
        if form.data == self.new_password.data:
            raise ValidationError('Original and New Passwords cannot be the same!') # new password should not be the same as the old one
        if self.new_password.data != self.confirm.data:
            raise ValidationError('New Password does not match! Type again!') # check to make sure that the two password fields match

class DeleteForm(FlaskForm):
    password = PasswordField('', 
                             validators=[DataRequired()], 
                             render_kw={"placeholder": "Enter Password"}) # password needed to delete account
    submit = SubmitField('Delete')

    def validate_password(self, form):
        if not check_password_hash(current_user.password, form.data): # compare hash of the submitted password to the hash in the db to ensure that they match
            raise ValidationError('Incorrect password')