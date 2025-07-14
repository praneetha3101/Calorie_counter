from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
        flash('User already exists.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/exercise', methods=['POST'])
@login_required
def exercise():
    age = int(request.form['age'])
    height = float(request.form['height'])
    weight = float(request.form['weight'])
    activity_level = request.form['activity_level']

    # Calculate BMR
    bmr = 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)

    exercise_suggestions = {
        'low': ['Walking', 'Light Yoga', 'Stretching', 'Tai Chi'],
        'medium': ['Jogging', 'Swimming', 'Cycling', 'Aerobics'],
        'high': ['Running', 'High-Intensity Interval Training (HIIT)', 'CrossFit', 'Competitive Sports']
    }

    return render_template('exercise.html', bmr=bmr, activity_level=activity_level, suggestions=exercise_suggestions[activity_level])

@app.route('/food', methods=['POST'])
@login_required
def food():
    bmr = float(request.form['bmr'])
    activity_level = request.form['activity_level']

    # Load the dataset
    df = pd.read_csv("C:\\Users\\PraneethaReddy\\Desktop\\calt\\calt\\caltracker\\dataset.csv")

    
    # Filter the dataset for the food items
    food_items = df.to_dict(orient='records')

    return render_template('food.html', bmr=bmr, activity_level=activity_level, food_items=food_items)

@app.route('/result', methods=['POST'])
@login_required
def result():
    bmr = float(request.form['bmr'])
    selected_food = request.form.getlist('food')

    # Load the dataset
    df = pd.read_csv("C:\\Users\\PraneethaReddy\\Desktop\\calt\\calt\\caltracker\\dataset.csv")
    
    # Calculate total calories consumed
    total_calories = sum(df[df['foodname'].isin(selected_food)]['calories'])

    # Calculate the 5% range
    lower_limit = bmr * 0.95
    upper_limit = bmr * 1.05

    # Determine calorie balance
    if total_calories < lower_limit:
        deficit = lower_limit - total_calories
        result = f"deficit by {deficit:.2f} calories"
        suggestions = df[df['calories'] <= deficit].sort_values(by='calories', ascending=False).head(5).to_dict(orient='records')
    elif total_calories > upper_limit:
        surplus = total_calories - upper_limit
        result = f"excess by {surplus:.2f} calories"
        suggestions = []
    else:
        result = "sufficient"
        suggestions = []

    return render_template('result.html', bmr=bmr, total_calories=total_calories, result=result, suggestions=suggestions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
