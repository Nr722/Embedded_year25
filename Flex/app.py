from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, emit
import os
import random
import time

app = Flask(__name__)

# -----------------------------------------------------------------------------  
# CONFIG  
# -----------------------------------------------------------------------------
app.config['SECRET_KEY'] = 'CHANGE_ME_TO_SOMETHING_SECURE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flex_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize SocketIO with your Flask app.
socketio = SocketIO(app)

# Global list to store live sensor data (if needed)
live_workout_data = []

# -----------------------------------------------------------------------------  
# DATABASE MODEL  
# -----------------------------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------------------------------------------------------  
# ROUTES  
# -----------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/post_data', methods=['POST'])
def post_data():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No JSON data provided"}), 400

    print("Received JSON data via HTTP POST:")
    print(json_data)
    
    live_workout_data.append(json_data)
    socketio.emit('sensor_data', json_data)
    
    return jsonify({
        "message": "Data received successfully",
        "data": json_data
    }), 200

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/ml_feedback')
@login_required
def ml_feedback():
    return jsonify(live_workout_data)

# --- Authentication Routes ---
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
# SOCKET.IO EVENT HANDLERS
# -----------------------------------------------------------------------------
@socketio.on('connect')
def handle_connect():
    print('A client connected. SID:', request.sid)

@socketio.on('sensor_data')
def handle_sensor_data(data):
    print("Received sensor data via Socket.IO:", data)
    # Simply emit the event to all connected clients
    socketio.emit('sensor_data', data)

@socketio.on('disconnect')
def handle_disconnect():
    print('A client disconnected. SID:', request.sid)

# -----------------------------------------------------------------------------
# BACKGROUND TASK (Optional for testing without the Raspberry Pi)
# -----------------------------------------------------------------------------
def background_thread():
    while True:
        time.sleep(0.2)
        data = {
            'timestamp': time.time(),
            'pitch': round(random.uniform(0, 90), 2)
        }
        print("Emitting dummy data:", data)
        socketio.emit('sensor_data', data)

# Uncomment to test dummy data:
# socketio.start_background_task(background_thread)

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    