# use this script to generate random data and write it to the Firebase database
import requests
import time
import random

db = "https://eslabtest-eae29-default-rtdb.firebaseio.com/"

for day in range(1, 10):  # Loop through 9 days
    for set_num in range(1, 4):  # Assume each day has 3 sets
        print(f"Writing to database: Day {day}, Set {set_num}")
        for rep_num in range(1, 4):  # Assume each set has 3 reps
            x = random.randrange(0, 10)
            y = random.randrange(0, 10)
            z = random.randrange(0, 10)
            data = {"x": x, "y": y, "z": z}
            
            url = f"{db}sensorData/{day}/{set_num}/{rep_num}.json"
            response = requests.put(url, json=data)
            
            if response.ok:
                print(f"Data written successfully for Day {day}, Set {set_num}, Rep {rep_num}")
            else:
                raise ConnectionError(f"Could not write to database at {url}")
            
            time.sleep(1)  # Reduce sleep time to 1 second for faster execution
