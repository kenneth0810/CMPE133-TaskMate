from app import myapp, db, login
from app.forms import LoginForm, RegistrationForm, TaskForm, PasswordForm, DeleteForm # all forms are from app.forms and handle all the form submission validations
from app.models import User, Task, Profile
#from app.preprocessing_data import preprocess_data
from flask import jsonify, render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from sqlalchemy import desc
#import pandas as pd
from datetime import datetime
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.preprocessing import LabelEncoder
#from sklearn.preprocessing import MinMaxScaler
#from sklearn.metrics.pairwise import cosine_similarity
#from nltk.corpus import stopwords
#from nltk.stem import PorterStemmer
#import numpy as np

# landing page
@login.user_loader
def load_user(id):
    return User.query.get(int(id)) # used for login logic

# landing page 
@myapp.route('/') # default route of websites but will redirect to other routes based on if a user is signed in or not
def index():
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    else:
        return redirect(url_for('login'))

@myapp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('An Account Is Already Logged In')
        print("Current User:", current_user)
        return redirect(url_for('index')) # registration page should not be accessible when a user is logged in
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first(): # cannot use an email that is already associated with another account
            flash('This email is already registered. Please login or use another email.', 'danger')
        else:
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data) # create new user entry
            user.set_password(form.password.data) # set password using a hashing function
            db.session.add(user) # add to db
            db.session.commit() # commit to db

            flash(f'Successfully registered account for {user.email}', 'success')
            login_user(user)

            return redirect(url_for('index'))
    return render_template('register.html', form=form)


@myapp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('An Account Is Already Logged In')
        print("Current User:", current_user)
        return redirect(url_for('tasks')) # login page should not be accessible when a user is logged in

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() # find the user in the db
        if user != None:
            if user.check_password(form.password.data): # check hashed password with the stored hash
                login_user(user) # login user from the session
                flash('Logged in successfully!', 'success')
                next_page = request.form.get('next') # some pages require being logged in so this parameter keeps track of previous pages to redirect to after loggin in
                if next_page:
                    return redirect(next_page) # redirect to a page other than the Tasks page
                else:
                    return redirect(url_for('tasks')) # redirect to Tasks by default
            else:
                flash("Incorrect Password", 'danger')  # user with email found but the password password is incorrect
        else:
            flash("No record of account under the entered email", 'danger') # inform that user account was not found for the email

    return render_template('login.html', form=form)

@myapp.route('/logout')
@login_required
def logout():
    logout_user() # logout user from the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@myapp.route('/tasks', methods = ['GET', 'POST'])
@login_required
def tasks():
    form = TaskForm()
    if form.validate_on_submit():
        edit_task_id = request.form.get('entry') # adding task and editing task logic can be combined by keeping track of the id of the task to edit (set to 0 if it's add task)
        if edit_task_id == "0": # if edit_task_id isn't greater than 0, then it's a regular add task action
            # add new task
            task = Task(user_id=current_user.id, title=form.title.data, description=form.description.data, priority=form.priority.data, due_date=form.due_date.data, due_time=form.due_time.data) # create new task entry with the form details
            db.session.add(task) # add task to db
            db.session.commit() # commit
            flash('Successfully created new task.')
            return redirect(url_for('tasks'))
        else:
            # edit task
            findTask = Task.query.filter_by(id=edit_task_id).first() # find task with id
            form.populate_obj(findTask) # edit the db with the edited task information
            db.session.commit() # commit
    tasks = Task.query.filter(Task.user_id==current_user.id).order_by(desc(Task.priority)).all() # list of all tasks ordered by priority first then by when each were added
    for t in tasks:
        if (t.due_date):
            t.due_date = t.due_date.strftime("%m/%d/%Y") # reformat date so that the frontend can read it
        if (t.due_time):
            t.due_time = t.due_time.strftime("%I:%M %p") # reformat time so that the frontend can read it
    form.process() # reset most of the form fields to blank once the new task has been added to the db

    # Count task frequencies based on how many times a task title repeats
    task_counts = {}
    num_incomplete = 0 # keep track of # of tasks incomplete or in progress
    for task in tasks:
        if task.title not in task_counts:
            task_counts[task.title] = {'count': 0, 'task_obj': task}
        task_counts[task.title]['count'] += 1 # increment title count
        if task.is_completed == False:
            num_incomplete += 1 # incremement incomplete count

    # Sort tasks by frequency and select top 5
    top_n_tasks = sorted(task_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:5] # Find the 5 most frequent titles
    print(top_n_tasks)

    # Create a list of dictionaries for common tasks
    common_tasks = [task[1]['task_obj'] for task in top_n_tasks] # render a list of the Task entry objects with the 5 most frequent titles
    print(common_tasks)

    return render_template('tasks.html', form=form, tasks=tasks, common_tasks=common_tasks, num_incomplete=num_incomplete)


@myapp.route('/delete_task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first() # find the task with the parameter id
    db.session.delete(task) # delete the found task from the db
    db.session.commit() # commit
    return jsonify({'success': True, 'message': f'Task {task_id} successfully deleted.'})

@myapp.route('/edit_task/<task_id>', methods=['GET'])
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id).first() # find the task with the parameter id
    task_dict = {key: value for key, value in task.__dict__.items() if not key.startswith('_')} # render a dictionary of task entry details
    if task_dict['due_date']:
        task_dict['due_date'] = task_dict['due_date'].strftime("%Y-%m-%d") # reformat date so that the frontend can read it
    if task_dict['due_time']:
        task_dict['due_time'] = task_dict['due_time'].strftime("%H:%M") # reformat date so that the frontend can read it
    return jsonify({'success': True, 'message': f'Task {task_id} details retrieved.', 'task': task_dict})

@myapp.route('/complete_task/<task_id>', methods=['PATCH'])
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id).first() # find the task with the parameter id
    task.is_completed = True # set the found task's is_completed field to true
    db.session.commit() # commit
    return jsonify({'success': True, 'message': f'Task {task_id} successfully marked as complete.'})

@myapp.route('/recover_task/<task_id>', methods=['PATCH'])
def recover_task(task_id):
    task = Task.query.filter_by(id=task_id).first() # find the task with the parameter id
    task.is_completed = False # set the found task's is_complete field to false so that it will now be an incomplete or in progress task
    db.session.commit() # commit
    return jsonify({'success': True, 'message': f'Task {task_id} successfully marked as incomplete.'})

print("URL Map", myapp.url_map)

@myapp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    pw_form = PasswordForm()
    if (pw_form.old_password.data != None or pw_form.new_password.data != None or pw_form.confirm.data != None) and pw_form.validate_on_submit() and request.method == "POST": # ignore form if the fields are all empty (when there is only a submission for deleting account) but validate otherwise
        user = current_user
        if user.check_password(pw_form.old_password.data): # check the hashed password with the stored hash from the db in order to proceed
            if not user.check_password(pw_form.new_password.data):
                user.set_password(pw_form.new_password.data)
                db.session.commit()
                flash('Successfully Reset Password.')
                return redirect(url_for('account'))
    
    #deletes every row from models.py tables that belongs to the current user
    delete_form = DeleteForm()
    if delete_form.password.data != None and delete_form.validate_on_submit() and request.method == "POST": # ignore form if the field is all empty (when there is onlt a submission for password change) but validate otherwise
        user = current_user
        if user.check_password(delete_form.password.data):
            deleteTasks = Task.query.filter_by(user=current_user).all()
            for task in deleteTasks:
                db.session.delete(task)
                db.session.commit()

            b = Profile.query.filter_by(user_id=current_user.id).first()
            if b:
                db.session.delete(b)
                db.session.commit()

            db.session.delete(user)
            db.session.commit()
            logout_user
            flash('Successfully Deleted Account.')
            return redirect(url_for('register')) 
            # user will get redirected to registration page when an account is deleted
        else:
            flash('Incorrect Password!')
    return render_template('account.html', pform=pw_form, user=current_user, dform=delete_form)

"""@myapp.route('/predic', methods=['GET', 'POST'])
@login_required
def convert_to_dataframe():
    # Query all tasks:
    tasks = Task.query.filter(Task.user_id==current_user.id).all()
    
    # Extract each task from SQLAlchemy "Task" objects
    data_of_task = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'due_date': task.due_date,
        'due_time': task.due_time,
        'is_completed': task.is_completed
    } for task in tasks]
    
    # Create the DataFrame based on a list of dictionaries: data_of_tasks
    df = pd.DataFrame(data_of_task)
    


    # Normalize numerical features
    scaler = MinMaxScaler()
    priority_scaled = scaler.fit_transform(df[['priority']].astype(float))
    due_date_scaled = scaler.fit_transform(df[['due_date']].astype(int).values.reshape(-1, 1))

    # Combine all features into a single matrix
    features = np.hstack([tfidf_matrix.toarray(), priority_scaled, due_date_scaled])
    print("Feature Matrix Shape:", features.shape)

    # Compute cosine similarity matrix
    cosine_sim = cosine_similarity(features, features)
    print("Cosine Similarity Matrix Shape:", cosine_sim.shape)

    # Return the DataFrame as a JSON response
    return features
"""
