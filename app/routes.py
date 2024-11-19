from app import myapp, db, login
from app.forms import LoginForm, RegistrationForm, TaskForm
from app.models import User, Task
from flask import jsonify, render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
import pandas as pd
from sklearn.preprocessing import LabelEncoder

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

@myapp.route('/tasks', methods = ['GET', 'POST'])
@login_required
def tasks():
    form = TaskForm()
    if form.validate_on_submit():
        edit_task_id = request.form.get('entry')
        print(edit_task_id)
        if edit_task_id == "0": # if edit_task_id isn't greater than 0, then it's a regular add task action
            task = Task(user_id=current_user.id, title=form.title.data, description=form.description.data, priority=form.priority.data, due_date=form.due_date.data, due_time=form.due_time.data)
            db.session.add(task)
            db.session.commit()
            flash('Successfully created new task.')
            tasks = Task.query.filter(Task.user_id==current_user.id).filter(Task.is_completed==False).all()
            return redirect(url_for('tasks'))
        else:
            findTask = Task.query.filter_by(id=edit_task_id).first()
            form.populate_obj(findTask)
            db.session.commit()
    tasks = Task.query.filter(Task.user_id==current_user.id).filter(Task.is_completed==False).all()
    return render_template('tasks.html', form=form, tasks=tasks)

@myapp.route('/delete_task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Task {task_id} successfully deleted.'})

@myapp.route('/edit_task/<task_id>', methods=['GET'])
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task_dict = {key: value for key, value in task.__dict__.items() if not key.startswith('_')}
    return jsonify({'success': True, 'message': f'Task {task_id} details retrieved.', 'task': task_dict})

@myapp.route('/complete_task/<task_id>', methods=['PATCH'])
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.is_completed = True
    db.session.commit()
    return jsonify({'success': True, 'message': f'Task {task_id} successfully marked as complete.'})

print("URL Map", myapp.url_map)

