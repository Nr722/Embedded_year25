import requests

# Firebase Realtime Database URL
db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"

def get_fire(date=None, set_number=None):
    """Fetch workout data from Firebase.
    
    Args:
        date (str): (Optional) Specific date in 'YYYY-mm-dd' format. If not provided, fetches all dates.
        set_number (int): (Optional) Specific set number to fetch (e.g., 1 for 'set1'). If not provided, fetches all sets for the given date.
    
    Returns:
        dict: The fetched data from Firebase.
    """
    # Construct the URL
    if date and set_number:
        request_url = f"{db}{date}/set{set_number}.json"
    elif date:
        request_url = f"{db}{date}.json"
    else:
        request_url = f"{db}.json"

    print(f"Fetching data from: {request_url}")  # Debugging log
    
    # Make the GET request
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


print(get_fire())