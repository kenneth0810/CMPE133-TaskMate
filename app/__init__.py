from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

myapp = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

myapp.config.from_mapping(
    SECRET_KEY = os.getenv('SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False
)

db = SQLAlchemy(myapp)

with myapp.app_context():
    db.create_all()

login = LoginManager(myapp)

login.login_view = 'login'

from app import routes, models