import requests

db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"
path = "workouts.json"

def get_fire(timestamp=None):
    """Fetches workout data from the Firebase database."""
    # Construct request URL
    request_url = db + "workouts.json"
    if timestamp:
        request_url = f"{db}workouts/{timestamp}.json"
    
    print(f"Fetching data from: {request_url}")  # Debugging log
    
    # Make the request
    response = requests.get(request_url)
    
    # Handle the response
    if response.ok:
        data = response.json()
        if data:
            print("Data fetched successfully.")
            return data
        else:
            print("Request successful but no data found.")
            return {}
    else:
        raise ConnectionError(f"Could not access database: {response.status_code} - {response.text}")

# Example call: Fetch all data
all_data = get_fire()

def parse_workout_data(workout_data):
    """Parses workout data to extract all reps and their fields."""
    for set_key, reps in workout_data.items():
        print(f"Set: {set_key}")
        for rep_key, rep_data in reps.items():
            print(f"  Rep: {rep_key}, Data: {rep_data}")

# Example usage
timestamp = "1"  # Replace with an actual timestamp
specific_data = get_fire(timestamp)
if specific_data:
    parse_workout_data(specific_data)
