from app import myapp, login, db
from datetime import datetime
from time import time
from sqlalchemy.types import Boolean, Date, DateTime, Float, Integer, Text, Time, Interval
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
import base64

# Set up the table User with different columns in Database:
class User(db.Model, UserMixin):
    # User's ID:
    id = db.Column(db.Integer, primary_key=True)
    # Username:
    username = db.Column(db.String(32), nullable=False)
    # User's password:
    password = db.Column(db.String(32), nullable=False)
    # User's email:
    email = db.Column(db.String(100), nullable=False, unique=True)

    # Set up relationship with class Post:
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # Relationship with Reminders:
    tasks = db.relationship("Task", backref="user", lazy="dynamic")

    # Function which generates password hash for user's password --> more protected!
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Function which checks the hash of password given by user and the password in Database:
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Function which generates a reset password token for the user:
    # The token will expire after 600 seconds (10 mins)
    def get_reset_password_token(self, expires_in=600):
        # Generates token by using the encode() method of PyJWT package: 
        return jwt.encode(
            # The dictionary below contains the data which will be encoded
            # with our Flask app's secret key to sign the token
            # and hashing algorithm 'HS256' for that token signature:
            {'reset_password': self.id, 'exp': time() + expires_in},
            myapp.config['SECRET_KEY'], algorithm='HS256')

    # This static method verifies 1 reset password token then returns corresponding user:
    @staticmethod
    def verify_reset_password_token(token):
        try:
            # Decoding token by decode() method in PyJWT package:
            id = jwt.decode(token, myapp.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            # If the token is invalid (or has been already expired) --> None:
            return
        # If the token is valid --> the user object corresponding to the user id in the token.
        return User.query.get(id)

    # Function that returns 1 string every time creating 1 new row (user): 
    def __repr__(self):
        return f'<User {self.id}: {self.username}, {self.fullname}>'

# Set up the table Post with different columns in Database:
class Post(db.Model):
    # Post ID:
    id = db.Column(db.Integer, primary_key=True)
    # Post Body:
    body = db.Column(db.String(256))
    # Post timestamp:
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    # Set up relationship with class User:
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Function that returns 1 string every time creating 1 new Post element in Database:
    def __repr__(self):
        return f'<Post {self.id}: {self.body}>'

# Database for representing a reminder in the reminder application with different columns
class Task(db.Model):
    # Task ID:
    id = db.Column(db.Integer, primary_key=True)
    # Task Title:
    title = db.Column(db.String(255), nullable=False)
    # Task Description:
    description = db.Column(db.Text)
    # Task Priority:
    priority = db.Column(db.String(10), nullable=True)  # Values like 'low', 'medium', 'high'
    # Task Due Date:
    due_date = db.Column(db.Date, nullable=False)
    # Task Due Time:
    due_time = db.Column(db.Time, nullable=False)
    # Task Status
    is_completed = db.Column(db.Boolean, default=False)
    

    # Foreign Key relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Task: {self.title} - {self.due_date} - {self.due_time} - {self.priority}>"

# Create all the tables by calling create_all() method of the db object 
# within the application context to ensure that the app's database connection is available:
with myapp.app_context():
    db.create_all()

# This is a callback function used by Flask-Login to load a user from a user ID.
# The 'id' argument is the user ID as a string, 
# which we convert to an integer before querying the database for the user:
@login.user_loader
# The function returns a User object or None if no user is found with the given ID.
def load_user(id):
    return User.query.get(int(id))
