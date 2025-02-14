import requests
import time

db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"
path = "workouts.json"

def get_fire():
    # Full request URL (fetch all workouts)
    request_url = db + path
    print(f"Fetching data from: {request_url}")  # Debugging log
    
    # Make the request
    response = requests.get(request_url)
    
    # Handle the response
    if response.ok:
        data = response.json()
        if data:
            print(f"Request successful. Retrieved {len(data)} workouts.")
            
            # Iterate over workouts
            for workout_key, workout in data.items():
                print(f"\nWorkout: {workout_key}")
                
                # Iterate over sets in each workout
                for set_key, set_data in workout.items():
                    print(f"  Set: {set_key}")
                    
                    # Iterate over reps in each set
                    for rep_key, rep_data in set_data.items():
                        print(f"    Rep: {rep_key}")
                        print(f"      max_pitch: {rep_data.get('max_pitch')}")
                        print(f"      max_gz_up: {rep_data.get('max_gz_up')}")
                        print(f"      max_az: {rep_data.get('max_az')}")
                        print(f"      max_gz_down: {rep_data.get('max_gz_down')}")
                        
            return data
        else:
            print("Request successful but no data found.")
            return {}
    else:
        raise ConnectionError(f"Could not access database: {response.status_code} - {response.text}")

# Example call
# data = get_fire()
