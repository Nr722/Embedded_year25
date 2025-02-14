from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, emit
import os, random, time, json, subprocess
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler


app = Flask(__name__) 
CORS(app)            

# Define file path (ensure this path exists)
JSON_FILE_PATH = "/home/ubuntu/metrics.json"
SCRIPT_PATH = "/home/ubuntu/k_means_clustering.py"
OUTPUT_FILE_PATH = "/home/ubuntu/processed_output.json"

# -----------------------------------------------------------------------------  
# CONFIG  
# -----------------------------------------------------------------------------
app.config['SECRET_KEY'] = 'CHANGE_ME_TO_SOMETHING_SECURE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flex_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


socketio = SocketIO(app)


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
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

# -----------------------------------------------------------------------------
@app.route('/save_metrics', methods=['POST'])
def save_metrics():
    try:
        
        data = request.json
        print("Received data:", data)  
        with open(JSON_FILE_PATH, "w") as json_file:
            json.dump(data, json_file, indent=4)

        
        result = subprocess.run(["python3", SCRIPT_PATH], capture_output=True, text=True)
        print("Processing Script Output:", result.stdout)
        print("Processing Script Error (if any):", result.stderr)

        # Check if processing script created an output file
        if os.path.exists(OUTPUT_FILE_PATH):
            with open(OUTPUT_FILE_PATH, "r") as output_file:
                processed_data = json.load(output_file)
        else:
            processed_data = {"error": "Processing script did not generate output"}

        return jsonify({
            "status": "success",
            "message": "Metrics saved and processed successfully",
            "processed_data": processed_data
        })

    except Exception as e:
        print("Error in /save_metrics:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_processed_results', methods=['GET'])
def get_processed_results():
    """Returns the processed data from the Python script"""
    try:
        if os.path.exists(OUTPUT_FILE_PATH):
            with open(OUTPUT_FILE_PATH, "r") as output_file:
                processed_data = json.load(output_file)
            return jsonify(processed_data)
        else:
            return jsonify({"error": "Processed data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# API endpoint to run K-Means and return results
@app.route('/run-kmeans', methods=['GET'])
def run_kmeans(data):
    result = perform_kmeans(data)
    return jsonify(result)

def perform_kmeans(data):

    
    new_df = pd.DataFrame(data)


    features = ['max_pitch', 'max_gz_up', 'max_az', 'max_gz_down']
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    new_df['cluster'] = kmeans.fit_predict(new_df[features])
    
    
    cluster_averages = new_df.groupby('cluster')['max_pitch'].mean()
    label_mapping = {}
    if cluster_averages.iloc[0] > cluster_averages.iloc[1]:
        label_mapping = {cluster_averages.index[0]: 'good', cluster_averages.index[1]: 'fatigued'}
    else:
        label_mapping = {cluster_averages.index[0]: 'fatigued', cluster_averages.index[1]: 'good'}
    
    
    new_df['performance'] = new_df['cluster'].map(label_mapping)
    

    new_perf_ratio = new_df['performance'].value_counts(normalize=True)
    new_perf_averages = new_df.groupby('performance').mean()


    hist_perf_ratio = pd.Series({
        'good': 0.70,
        'fatigued': 0.30
    })
    hist_perf_averages = pd.DataFrame({
        'peak_ang_vel_up': {'good': 0.65, 'fatigued': 0.55},
        'range_of_motion': {'good': 1.0, 'fatigued': 0.9},
        'shoulder_movement': {'good': 0.50, 'fatigued': 0.60},
        'peak_ang_vel_down': {'good': 0.35, 'fatigued': 0.40}
    })


    new_perf_averages = new_perf_averages.rename(columns={
        'max_gz_up': 'peak_ang_vel_up',
        'max_pitch': 'range_of_motion',
        'max_az': 'shoulder_movement',
        'max_gz_down': 'peak_ang_vel_down'
    })


    recommendations = []

    recommendations.append("\nOverall Recommendations:")
    if new_perf_ratio.get('fatigued', 0) > hist_perf_ratio.get('fatigued', 0):
        recommendations.append("  - You performed a higher percentage of fatigued reps compared to your historical data. Consider reviewing your recovery protocols or adjusting your workout intensity.")
    else:
        recommendations.append("  - Your percentage of fatigued reps is in line with or below your historical average. Keep up the good work on recovery.")

    # Further recommendations for 'good' reps
    if ('good' in new_perf_averages.index) and ('good' in hist_perf_averages.index):
        if new_perf_averages.loc['good', 'peak_ang_vel_up'] < hist_perf_averages.loc['good', 'peak_ang_vel_up']:
            recommendations.append("  - For your 'good' reps, the peak upward velocity is slightly lower than usual. You might consider incorporating power or speed work to improve explosive strength.")

    # Extended logic for 'good' reps: Range of Motion and Shoulder Movement
    if ('good' in new_perf_averages.index) and ('good' in hist_perf_averages.index):
        if new_perf_averages.loc['good', 'range_of_motion'] < 0.95 * hist_perf_averages.loc['good', 'range_of_motion']:
            recommendations.append("  - Your average range of motion for 'good' reps has decreased more than 5% compared to your historical average. Consider mobility work.")
        if new_perf_averages.loc['good', 'shoulder_movement'] > 1.05 * hist_perf_averages.loc['good', 'shoulder_movement']:
            recommendations.append("  - Your shoulder movement for 'good' reps is higher than your historical average. Focus on strict form to isolate the targeted muscles.")

    # Recommendations for 'fatigued' reps
    if ('fatigued' in new_perf_averages.index) and ('fatigued' in hist_perf_averages.index):
        if new_perf_averages.loc['fatigued', 'range_of_motion'] < hist_perf_averages.loc['fatigued', 'range_of_motion']:
            recommendations.append("  - Your range of motion in 'fatigued' reps is lower than your historical norm. Consider lighter weights or more rest.")
        if new_perf_averages.loc['fatigued', 'shoulder_movement'] > hist_perf_averages.loc['fatigued', 'shoulder_movement']:
            recommendations.append("  - Your shoulder involvement in 'fatigued' reps is higher than usual. Focus on strict technique.")
        if new_perf_averages.loc['fatigued', 'peak_ang_vel_down'] > hist_perf_averages.loc['fatigued', 'peak_ang_vel_down']:
            recommendations.append("  - Your peak downward velocity on fatigued reps is higher than historical averages. Slow the negative phase for better control.")

    fatigued_diff = (new_perf_ratio.get('fatigued', 0) - hist_perf_ratio.get('fatigued', 0)) * 100
    if fatigued_diff > 10:
        recommendations.append(f"  - There's a significant (+{fatigued_diff:.1f}%) jump in fatigued reps. Consider shorter sets or longer rests.")
    elif fatigued_diff < -5:
        recommendations.append(f"  - Nice improvement! You reduced your fatigued reps by {-fatigued_diff:.1f}%. Keep it up.")

    result = {
        'recommendations': recommendations
    }
    return result
