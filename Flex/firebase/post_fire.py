import requests
import json

db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"
path = "workouts.json"

def post_fire(workout_key, set_key, rep_data):
    # Construct the path for the specific workout and set
    post_url = f"{db}workouts/{workout_key}/{set_key}.json"
    
    # Post request to push a new rep under the set
    response = requests.post(post_url, data=json.dumps(rep_data))
    
    # Handle response
    if response.ok:
        print(f"Data posted successfully")
        return response.json()  # Return the response with the generated key
    else:
        raise ConnectionError(f"Failed to post data: {response.status_code} - {response.text}")

# Example data to post
rep_data_example = {
    'max_pitch': 0.75,
    'max_gz_up': 0.55,
    'max_az': 0.35,
    'max_gz_down': 0.25
}

# Example usage
# post_fire("workout1", "set1", rep_data_example)
