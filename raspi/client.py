import math
import requests
import datetime

def sanitize_data(rep_data):
    """Replace infinite or NaN values with 0 (or any valid number)."""
    sanitized = {}
    for key, value in rep_data.items():
        if isinstance(value, float):
            if math.isinf(value) or math.isnan(value):
                sanitized[key] = 0  # Replace with a default value of your choice
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value
    return sanitized

class FirebaseClient:
    def __init__(self, db_url):
        self.db_url = db_url.rstrip('/') + '/'  # Ensure trailing slash
        
        self.current_date = datetime.date.today().strftime('%Y-%m-%d')
        
        date_url = f"{self.db_url}{self.current_date}.json"
        response = requests.get(date_url)
        if response.ok:
            date_data = response.json()
            if date_data is None:
                self.set_number = 1
            else:
                sets = [key for key in date_data.keys() if key.startswith("set")]
                if sets:
                    max_set = max(int(s.replace("set", "")) for s in sets)
                    self.set_number = max_set + 1
                else:
                    self.set_number = 1
        else:
            raise ConnectionError("Could not retrieve data for date: " + self.current_date)
        
        print(f"FirebaseClient initialized: Date = {self.current_date}, Set = {self.set_number}")

    def send_rep_data(self, rep_data):
        """
        Sends aggregated rep data to Firebase.
        The data will be stored under a path structured as:
          <db_url>/<date>/set<set_number>/rep<rep_number>.json
        """
        rep_data = sanitize_data(rep_data)
        rep_number = rep_data.get("rep_number", 0)
        
        url = f"{self.db_url}{self.current_date}/set{self.set_number}/rep{rep_number}.json"
        response = requests.put(url, json=rep_data)
        if response.ok:
            print(f"Data written successfully for rep {rep_number} in set {self.set_number} on {self.current_date}")
        else:
            raise ConnectionError(f"Could not write to database at {url}")
