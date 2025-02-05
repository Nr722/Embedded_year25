from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import os
import random

app = Flask(__name__)

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
app.config['SECRET_KEY'] = 'CHANGE_ME_TO_SOMETHING_SECURE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flex_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # If user not logged in, redirect to /login

# -----------------------------------------------------------------------------
# DATABASE MODEL
# -----------------------------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    # Gamification example
    score = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------------------------------------------------------
# MOCK ML DATA
# -----------------------------------------------------------------------------
def mock_ml_output():
    range_of_motion = random.choice(["Good", "Average", "Bad"])
    time_under_tension = round(random.uniform(1.0, 5.0), 2)
    swinging = random.choice(["Minimal", "Moderate", "Excessive"])
    return {
        "range_of_motion": range_of_motion,
        "time_under_tension": time_under_tension,
        "swinging": swinging
    }

# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------

@app.route('/')
def home():
    """Public landing page with chart and animations."""
    return render_template('index.html')

@app.route('/post_data', methods=['POST'])
def post_data():
    # Attempt to retrieve JSON data from the request
    json_data = request.get_json()
    
    if not json_data:
        # If no JSON data was sent, return an error response
        return jsonify({"error": "No JSON data provided"}), 400

    # Print the received JSON data to the terminal (stdout)
    print("Received JSON data:")
    print(json_data)
    
    # Optionally, you can process the data here
    # For now, we'll just echo the data back in the response
    return jsonify({
        "message": "Data received successfully",
        "data": json_data
    }), 200


@app.route('/contact')
def contact():
    """Contact page - show basic info."""
    return render_template('contact.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard with live feed via script.js."""
    return render_template('dashboard.html')

@app.route('/ml_feedback')
@login_required
def ml_feedback():
    print("DEBUG: /ml_feedback was called!")     # Add
    data = mock_ml_output()
    print("Returning data:", data)               # Add
    return jsonify(data)

# --- Authentication ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Sign-up successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
