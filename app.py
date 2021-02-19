import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists('env.py'):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route('/')
@app.route('/get_tasks')
def get_tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template('tasks.html', tasks=tasks)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # check if username already exists
        existing_user = mongo.db.users.find_one({'username': request.form.get('username').lower()})
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password'))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session['user'] = request.form.get('username').lower()
        flash('Registration successful!')
        return redirect(url_for('profile', username=session['user']))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one({'username': request.form.get('username').lower()})

        if existing_user:
            if check_password_hash(existing_user['password'], request.form.get('password')):
                session["user"] = request.form.get("username").lower()
                flash(f"Welcome {request.form.get('username')}")
                return redirect(url_for('profile', username=session['user']))
            else:
                flash("Incorrect username or password")
                return redirect(url_for('login'))
        
        else:
            flash("Incorrect username or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    flash("You have been logged out")
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/profile/<username>')
def profile(username):
    username = mongo.db.users.find_one({'username': session['user']})['username']
    if session['user']:
        return render_template('profile.html', username=username)
    return redirect(url_for('login'))


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        is_urgent = 'on' if request.form.get('is_urgent') else 'off'
        task = {
            'category_name': request.form.get('category_name'),
            'task_name': request.form.get('task_name'),
            'task_description': request.form.get('task_description'),
            'is_urgent': is_urgent,
            'due_date': request.form.get('due_date'),
            'created_by': session['user']
        }
        mongo.db.tasks.insert_one(task)
        flash('Your new task has been added!')
        return redirect(url_for('get_tasks'))

    categories = mongo.db.categories.find().sort("category_name", 1) # sort by ascending
    return render_template('add_task.html', categories=categories)


@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if request.method == 'POST':
        is_urgent = 'on' if request.form.get('is_urgent') else 'off'
        submit = {
            'category_name': request.form.get('category_name'),
            'task_name': request.form.get('task_name'),
            'task_description': request.form.get('task_description'),
            'is_urgent': is_urgent,
            'due_date': request.form.get('due_date'),
            'created_by': session['user']
        }
        mongo.db.tasks.update({'_id': ObjectId(task_id)}, submit)
        flash('Your task has been updated!')
        return redirect(url_for('get_tasks'))

    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})

    categories = mongo.db.categories.find().sort("category_name", 1) # sort by ascending
    return render_template('edit_task.html', task=task, categories=categories)

@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    mongo.db.tasks.remove({'_id': ObjectId(task_id)})
    flash("Task successfully deleted!")
    return redirect(url_for('get_tasks'))


@app.route('/get_categories')
def get_categories():
    categories = list(mongo.db.categories.find().sort('category_name', 1))
    return render_template('categories.html', categories=categories)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category = {
            "category_name": request.form.get('category_name')
        }
        mongo.db.categories.insert_one(category)
        flash('New Category added!')
        return redirect(url_for('get_categories'))
    return render_template('add_category.html')


@app.route('/edit_category/<category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if request.method == 'POST':
        submit = {
            'category_name': request.form.get('category_name')
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category updated!")
        return redirect(url_for('get_categories'))

    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    return render_template('edit_category.html', category=category)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port = int(os.environ.get('PORT')),
        debug = True)