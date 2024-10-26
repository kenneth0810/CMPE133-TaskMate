from app import myapp, db, login
from app.forms import LoginForm, RegistrationForm, TaskForm
from app.models import User, Task
from flask import render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

# landing page
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# landing page 
@myapp.route('/')
def index():
    return render_template('index.html')


@myapp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('This email is already registered. Please login or use another email.', 'danger')
        else:
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            flash(f'Successfully registered account for {user.email}', 'success')
            login_user(user)

            return redirect(url_for('index'))
    return render_template('register.html', form=form)


@myapp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('An Account Is Already Logged In')
        print("Current User:", current_user)
        return redirect(url_for('index')) 

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user != None:
            if user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully!', 'success')
                next_page = request.form.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('index'))
            else:
                flash("Incorrect Password", 'danger')
        else:
            flash("No record of account under the entered email", 'danger')

    return render_template('login.html', form=form)

@myapp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@myapp.route('/account')
@login_required
def account():
    user_id = current_user.id
    email = current_user.email
    return render_template('account.html', id = email)

@myapp.route('/tasks')
@login_required
def tasks():
    form = TaskForm()
    if form.validate_on_submit():
        if form.title == None:
            flash('Task must have title.')
            return
        else:
            task = Task(title=form.title, description=form.description, priority=form.priority, due_date=form.due_date, due_time=form.due_time)
            db.session.add(task)
            db.session.commit()
    return render_template('tasks.html', form=form)

print("URL Map", myapp.url_map)