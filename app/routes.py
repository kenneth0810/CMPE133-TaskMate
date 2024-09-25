from app import myapp, db
# from app.forms *import the form classes here*
# from app.models *import the model classes here*
from flask import render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required


# landing page
@myapp.route('/')
def index():
    return render_template('index.html')