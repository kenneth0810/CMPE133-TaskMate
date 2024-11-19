from app import myapp, db, login
from app.forms import LoginForm, RegistrationForm, TaskForm
from app.models import User, Task
from datetime import datetime
from flask import render_template
from flask import redirect, request, session, url_for, jsonify
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
        if form.title.data == None:
            flash('Task must have title.')
        else:
            task = Task(user_id=current_user.id, 
                        title=form.title.data, 
                        description=form.description.data, 
                        priority=form.priority.data, 
                        due_date=form.due_date.data, 
                        due_time=form.due_time.data)
            db.session.add(task)
            db.session.commit()
            flash('Successfully created new task.')
            tasks = Task.query.filter(Task.user_id==current_user.id).all()
            return redirect(url_for('tasks'))
    tasks = Task.query.filter(Task.user_id==current_user.id).all()
    return render_template('tasks.html', form=form, tasks=tasks)

print("URL Map", myapp.url_map)

@myapp.route('/data_preprocessing', methods=['GET', 'POST'])
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
    
    # For testing DataFrame
    print("Before:\n")
    print(df)

    # Fill missing values 
    df['description'] = df['description'].fillna("No description provided")
    #df['priority'] = df['priority'].fillna(df['priority'].mode()[0])  # Fill with most frequent value
    df['priority'] = df['priority'].fillna('1')
    
    # Ensure 'due_date' is in datetime format and fill missing dates 
    df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce') 
    df['due_date'].fillna(pd.to_datetime('2099-12-31'), inplace=True)

    df['due_time'] = df['due_time'].fillna(pd.to_datetime('00:00:00').time())  # Placeholder for missing times

    
    # Display the DataFrame after filling missing values 
    print("After:\n")
    print(df)

    # Label Encoding for priority 
    label_encoder = LabelEncoder() 
    df['priority'] = label_encoder.fit_transform(df['priority']) 
    
    # Extract year, month, day from 'due_date' 
    df['due_year'] = df['due_date'].dt.year 
    df['due_month'] = df['due_date'].dt.month 
    df['due_day'] = df['due_date'].dt.day 
     
    # Combine 'due_date' and 'due_time' to extract hour and minute 
    df['due_time'] = df.apply(lambda x: pd.to_datetime(f"{x['due_date'].date()} {x['due_time']}"), axis=1) 
    df['due_hour'] = df['due_time'].dt.hour 
    df['due_minute'] = df['due_time'].dt.minute 
    
    # Calculate the number of days until the due date 
    current_date = datetime.now() 
    df['days_until_due'] = (df['due_date'] - current_date).dt.days 
    
    # Add a column for the day of the week 
    df['due_weekday'] = df['due_date'].dt.dayofweek # Monday=0, Sunday=6 
    
    # Display the DataFrame after feature engineering 
    print("\n")
    print(df[['id', 'title', 'description', 'priority', 'due_date', 'due_time', 'due_year', 'due_month', 'due_day', 'due_hour', 'due_minute', 'days_until_due', 'due_weekday', 'is_completed']])

    # Return the DataFrame as a JSON response
    return "Done"