from app import myapp, db, login
from app.forms import LoginForm, RegistrationForm, TaskForm, BioForm, PasswordForm, DeleteForm, SuggestTaskForm
from app.models import User, Task, Profile
#from app.preprocessing_data import preprocess_data
from flask import jsonify, render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
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
            tasks = Task.query.filter(Task.user_id==current_user.id).all()
            return redirect(url_for('tasks'))
        else:
            findTask = Task.query.filter_by(id=edit_task_id).first()
            form.populate_obj(findTask)
            db.session.commit()
    tasks = Task.query.filter(Task.user_id==current_user.id).all()
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

@myapp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    user_id = current_user.id
    email = current_user.email
    bio_form = BioForm()
    if bio_form.validate_on_submit() and request.method == "POST":
        #if a current bio exists and a new bio is submitted, delete the current bio and replace it with the new bio
        curr_bio = Profile.query.filter_by(user_id=current_user.id).first()
        if curr_bio:
            db.session.delete(curr_bio)
        new_bio = Profile(user_id=current_user.id, bio=bio_form.bio.data)
        db.session.add(new_bio)
        db.session.commit()
        flash('Successfully Updated a nNew Bio.')
        return redirect(url_for('account'))
    else:
        #if nothing is submitted, the bio form will be empty, so assign the form.bio to the current bio so that the bio will be visible in the profile
        curr_bio = Profile.query.filter_by(user_id=current_user.id).first()

        if curr_bio:
            bio_form.bio.data = curr_bio.bio
    
    pw_form = PasswordForm()
    if pw_form.validate_on_submit() and request.method == "POST":
        user = current_user
        if user.check_password(pw_form.old_password.data):
            if not user.check_password(pw_form.new_password.data):
                user.set_password(pw_form.new_password.data)
                db.session.commit()
                flash('Successfully Reset Password.')
                return redirect(url_for('account'))
    
    #deletes every row from models.py tables that belongs to the current user
    delete_form = DeleteForm()
    if delete_form.validate_on_submit() and request.method == "POST":
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
            return redirect(url_for('login'))
        else:
            flash('Incorrect Password!')
    return render_template('account.html', bform=bio_form, pform=pw_form, user=current_user, dform=delete_form)

@myapp.route('/delete-bio/<int:id>', methods=['GET','POST'])
@login_required
def delete_bio(id):
    b = Profile.query.filter(Profile.user_id == id).first()
    if b:
        db.session.delete(b) 
        db.session.commit()
        flash('Successfully Deleted Bio')
    else:
        flash('There is no bio to be deleted.')
    return redirect(url_for('account'))


@myapp.route('/predict', methods=['GET', 'POST'])
def predict():
    tasks = Task.query.all()

    # Count task frequencies
    task_counts = {}
    for task in tasks:
        task_counts[task.title] = task_counts.get(task.title, 0) + 1

    # Sort tasks by frequency and select top 5
    top_n_tasks = sorted(task_counts.items(), key=lambda x: -x[1])[:5]

    # Create a list of dictionaries for common tasks
    common_tasks = [{'title': task[0], 'description': ''} for task in top_n_tasks]

    # Pass suggested tasks to the template for rendering
    return render_template('predict.html', common_tasks=common_tasks)


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