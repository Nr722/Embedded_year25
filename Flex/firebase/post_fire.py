import requests
import time
import random

# Your Firebase Realtime Database URL, ending with a slash
db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"

def get_next_set_number(date_data):
    """
    Given the JSON data under a date, find the maximum set number
    (e.g. set1, set2, set3...) and return the next set number to use.
    """
    if not date_data:
        # No sets exist, return 1
        return 1
    
    set_numbers = []
    for key in date_data.keys():
        if key.startswith("set"):
            try:
                # key is something like "set2" -> integer 2
                num = int(key[3:])
                set_numbers.append(num)
            except ValueError:
                pass
    
    if set_numbers:
        return max(set_numbers) + 1
    else:
        return 1

def main():
    # 1) Get today's date as a string (YYYY-mm-dd)
    today = time.strftime("%Y-%m-%d")
    print(f"Today is {today}")
    
    # 2) Read existing data for today's date
    url_date_path = db + f"{today}.json"
    resp = requests.get(url_date_path)
    if not resp.ok:
        raise RuntimeError(f"Failed to read from {url_date_path}: {resp.text}")
    
    date_data = resp.json()  # Could be None if date doesn't exist
    if date_data is None:
        date_data = {}
    
    # 3) Determine the next set number
    next_set_num = get_next_set_number(date_data)
    set_key = f"set{next_set_num}"
    print(f"Using {set_key} for today's workout.")
    
    # Example: create 5 reps
    total_reps = 5
    
    for rep_index in range(1, total_reps + 1):
        rep_key = f"rep{rep_index}"
        
        # This is the actual data you want to store for this rep
        data = {
            'max_pitch': 0.75,
            'max_gz_up': 0.55,
            'max_az': 0.35,
            'max_gz_down': 0.25
        }
        # 4) PUT the data to the path:  /<today>/<setKey>/<repKey>.json
        # Using PUT will overwrite at repKey; 
        # if you prefer auto-generated keys, you can use POST (and handle the response).
        rep_url = db + f"{today}/{set_key}/{rep_key}.json"
        response = requests.put(rep_url, json=data)
        
        if response.ok:
            print(f"Created/updated: {today}/{set_key}/{rep_key}")
        else:
            raise RuntimeError(f"Could not write rep data: {response.text}")

    print("All reps for this set have been successfully created/updated.")

if __name__ == "__main__":
    main()
