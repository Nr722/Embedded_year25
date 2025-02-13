import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import random, csv, os, bcrypt

CSV_FILE_PATH = "offline_sensor_data.csv"
CERTIFICATE_PATH = "./embeddedproject-bc58c-firebase-adminsdk-fbsvc-73de3876eb.json"
# Initialize Firebase Admin SDK
cred = credentials.Certificate(CERTIFICATE_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()
"""
DB Schema
username -> email, password, workouts
workouts -> timestamp/date
timestamp/date -> set1, set2, set3, ...
set1 -> rep1, rep2, rep3, ...
rep1 -> range_of_motion, max_acceleration_upward, time_down, shoulder_movement
"""
#---------------------DATABSE HELPER FUNCTIONS---------------------#
def initialize_firestore():
    username = "randomusername"
    doc_ref = db.collection('Users').document(username)
    
    # Initialize user document with email and password
    doc_ref.set({
        "email": "randomuser@random.com",
        "password": "securepassword123",
        "created_at": firestore.SERVER_TIMESTAMP,
        "friends": []
    })
    
    print(f"User document initialized for username: {username}")
    initialize_workouts(username)

def initialize_workouts(username):
    # Simulate adding multiple workouts
    for i in range(2):  # Example: 2 workout sessions
        workout_date = (datetime.now()).strftime("%d-%m-%y")
        workout_ref = db.collection('Users').document(username).collection('Workouts').document(workout_date)
        
        workout_ref.set({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "description": f"Workout session {i+1}"
        })
        
        initialize_sets(workout_ref, 3)  # Each workout has 3 sets
        print(f"Workout initialized with date: {workout_date}")

def initialize_sets(workout_ref, num_sets):
    for set_number in range(1, num_sets + 1):
        set_ref = workout_ref.collection("Sets").document(f"Set{set_number}")
        
        set_ref.set({
            "set_number": set_number,
            "description": f"Set {set_number}"
        })
        
        initialize_reps(set_ref, 5)  # Each set has 5 reps
        print(f"Set{set_number} initialized")

def initialize_reps(set_ref, num_reps):
    for rep_number in range(1, num_reps + 1):
        rep_ref = set_ref.collection("Reps").document(f"Rep{rep_number}")
        
        # Simulated data for each rep
        rep_ref.set({
            "rep_number": rep_number,
            "range_of_motion": random.choice(["Good", "Average", "Poor"]),
            "max_acceleration_upward": round(random.uniform(1.0, 3.0), 2),
            "time_down": round(random.uniform(0.5, 2.0), 2),
            "shoulder_movement": random.choice(["Minimal", "Moderate", "Excessive"])
        })
        
        print(f"Rep{rep_number} initialized with random data")

# Initialize Firestore with user and workout data
#initialize_firestore()

def add_workout(user_id):
    workout_date = datetime.now().strftime("%d-%m-%y")
    workout_ref = db.collection('Users').document(user_id).collection('Workouts').document(workout_date)

    workout_ref.set({
        "timestamp": firestore.SERVER_TIMESTAMP,
        "description": f"Workout session on {workout_date}"
    }, merge=True)

    print(f"Workout created for user: {user_id} on {workout_date}")

def add_set(user_id, workout_date, set_number):
    set_ref = db.collection('Users').document(user_id).collection('Workouts').document(workout_date).collection('Sets').document(f"Set{set_number}")

    set_ref.set({
        "set_number": set_number,
        "description": f"Set {set_number}"
    }, merge=True)

    print(f"Set {set_number} added to workout on {workout_date} for user {user_id}")

def add_rep(user_id, workout_date, set_number, rep_number, rep_data):
    rep_ref = db.collection('Users').document(user_id).collection('Workouts').document(workout_date).collection('Sets').document(f"Set{set_number}").collection('Reps').document(f"Rep{rep_number}")

    rep_ref.set({
        "rep_number": rep_number,
        **rep_data
    }, merge=True)

    print(f"Rep {rep_number} added to Set {set_number} in workout on {workout_date} for user {user_id}")


#---------------------FUNCTIONS TO FETCH FROM DB-----------------------------#
def fetch_user_workout_data(user_id):
    user_ref = db.collection("Users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        print(f"User {user_id} does not exist in the database")
        return {}

    workouts = user_ref.collection("Workouts").stream()
    workout_data = {}

    for workout in workouts:
        workout_date = workout.id
        workout_data[workout_date] = {
            "timestampt": workout.to_dict().get("timestamp"),
            "description": workout.to_dict().get("description"),
            "sets": {}
        }

        sets = workout.reference.collection("Sets").stream()
        for set_doc in sets:
            set_number = set_doc.id
            workout_data[workout_date]["sets"][set_number] = {
                "set_number": set_doc.to_dict().get("set_number"),
                "description": set_doc.to_dict().get("description"),
                "reps": {}
            }

            reps = set_doc.reference.collection("Reps").stream()
            for rep_doc in reps:
                rep_number = rep_doc.id
                workout_data[workout_date]["sets"][set_number]["reps"][rep_number] = rep_doc.to_dict()
    
    return workout_data
#---------------------------------------------------------------------------#


#----------------------------------USER AUTHENTICATION FUNCTIONS---------------------------------#

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def add_user(user_id, email, password):
    hashed_password = hash_password(password)
    user_ref = db.collection("Users").document(user_id)

    user_ref.set({
        "email": email,
        "password": hashed_password.decode('utf-8'),
        "created_at": firestore.SERVER_TIMESTAMP,
    })

    print(f"User {user_id} added to DB")

def authenticate_user(user_id, password):
    user_ref = db.collection("Users").document(user_id)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        hashed_pswd = user_data["password"].encode('utf-8')
        if verify_password(password, hashed_pswd):
            print(f"User {user_id} authenticated")
            return True
        else:
            print(f"User {user_id} not authenticated")
            return False
    else:
        print(f"{user_id} not found in DB")
        return False
    
#-------------------------------------------------------------------------------------------------#

def upload_offline_data(user_id):
    """
    Upload offline sensor data from CSV to Firestore.

    Args:
        user_id (str): The ID of the user to whom the data belongs.
    """
    if not os.path.isfile(CSV_FILE_PATH):
        print("No offline data found.")
        return

    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Loop through each row and push to Firestore
        for row in reader:
            workout_date = datetime.fromtimestamp(float(row["timestamp"])).strftime("%d-%m-%y")
            set_number = "Set1"  # Adjust this logic if needed to determine the correct set number
            rep_number = f"Rep{int(float(row['timestamp']) % 10)}"  # Simple logic for rep number based on timestamp

            rep_data = {
                "timestamp": float(row["timestamp"]),
                "range_of_motion": row["range_of_motion"],
                "peak_an_vel_up": float(row["peak_an_vel_up"]),
                "peak_ang_vel_down": float(row["peak_ang_vel_down"]),
                "shoulder_movement": row["shoulder_movement"]
            }
            
            add_rep(user_id, workout_date, set_number, rep_number, rep_data)
    
    # Delete the CSV file after uploading to avoid reprocessing the same data
    os.remove(CSV_FILE_PATH)
    print("Offline data uploaded and CSV file deleted.")


def write_sensor_data_to_csv(data):
    """
    Write sensor data to a CSV file for offline storage.

    Args:
        data (dict): A dictionary with sensor data fields:
            {
                "timestamp": float (Unix timestamp),
                "range_of_motion": str,
                "peak_an_vel_up": float,
                "peak_ang_vel_down": float,
                "shoulder_movement": str
            }
    """
    file_exists = os.path.isfile(CSV_FILE_PATH)

    # Open the file in append mode
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writerow(["timestamp", "range_of_motion", "peak_an_vel_up", "peak_ang_vel_down", "shoulder_movement"])
        
        # Write the data row
        writer.writerow([
            data["timestamp"],
            data["range_of_motion"],
            data["peak_an_vel_up"],
            data["peak_ang_vel_down"],
            data["shoulder_movement"]
        ])
    
    print(f"Data written to {CSV_FILE_PATH}")



"""
Timing analysis of raspi
timefunction...
logic to calculate data from sensors
timefunction to time how long calculation takes
timefunction...
send data to webapp
timefunction to time how long it takes to receive 
acknowledgement from webapp

1. how fast is the calc of the kalman filter - 
compare to data sensor timing (sampling frequency) 
TIME UPDATE FUNCTION
2. speed of sending from raspi to web app 
so we keep the sensor interval similar or to how 
many fps we can show
TIME send_sensor_data FUNCTION
3. send rep data and bicep engagement over to web app


HANDLE OFFLINE FUNCTIONALITY ->
raspi function to write/create csv of sensor data
fucntion to parse CSV file with sensor data

range of motion, peak_an_vel_up, peak_ang_vel_down, shoulder movement
"""