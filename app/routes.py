from app import myapp, db, login
from app.forms import LoginForm
from app.models import User
from flask import render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# landing page!
@myapp.route('/')
def index():
    return render_template('index.html')