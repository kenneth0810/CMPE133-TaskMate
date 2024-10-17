from app import myapp, db, login
from app.forms import LoginForm, RegistrationForm
from app.models import User
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


@myapp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('This username is unavailable. Please use another username.')
        if User.query.filter_by(email=form.email.data).first():
            flash('This email is already registered. Please login or use another email.')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    return render_template('register.html', form=form)
