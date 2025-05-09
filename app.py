from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Todo
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('login'))
        new_user = User(email=email)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('User not found!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/index', methods=['GET'])
@login_required
def index():
    filter_type = request.args.get('filter', 'all')  # Default to 'all'
    
    if filter_type == 'active':
        todos = Todo.query.filter_by(user_id=current_user.id, completed=False).all()
    elif filter_type == 'completed':
        todos = Todo.query.filter_by(user_id=current_user.id, completed=True).all()
    else:
        todos = Todo.query.filter_by(user_id=current_user.id).all()  # All todos

    return render_template('index.html', todos=todos, filter=filter_type)


@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    description = request.form['description']
    new_todo = Todo(title=title, description=description, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>',methods=['POST'])
@login_required
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if todo and todo.user_id == current_user.id:
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>', methods=['POST'])
@login_required
def toggle(todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if todo:
        todo.completed = not todo.completed
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def update(todo_id):
    todo = Todo.query.get(todo_id)
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', todo=todo)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

