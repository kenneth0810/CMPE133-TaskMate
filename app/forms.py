from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from wtforms.widgets import TextArea
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

class BioForm(FlaskForm):
    bio = StringField("Bio:", 
                      validators = [DataRequired(), Length(max = 100)], 
                      render_kw ={"placeholder":"(Max: 100 characters) Add Bio Here"})
    submit = SubmitField("Save")

class PasswordForm(FlaskForm):
    old_password = PasswordField("", 
                                 validators = [DataRequired()], 
                                 render_kw ={"placeholder":"Enter Original Password"})
    new_password = PasswordField("", 
                                 validators=[DataRequired(), Length(min=4, max=10)], 
                                 render_kw={"placeholder": "Enter a New Password"}) 
    confirm = PasswordField("", 
                            validators=[DataRequired()], 
                            render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField("Update")

    def validate_old_password(self, form):
        if not check_password_hash(current_user.password, form.data):
            raise ValidationError('Incorrect Original Password!')
        if form.data == self.new_password.data:
            raise ValidationError('Original and New Passwords cannot be the same!')
        if self.new_password.data != self.confirm.data:
            raise ValidationError('New Password does not match! Type again!')

class DeleteForm(FlaskForm):
    password = PasswordField('', 
                             validators=[DataRequired()], 
                             render_kw={"placeholder": "Enter Password"})
    submit = SubmitField('Delete')

    def validate_password(self, form):
        if not check_password_hash(current_user.password, form.data):
            raise ValidationError('Incorrect password')