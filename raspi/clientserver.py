import math
import socketio  

def sanitize_data(sensor_data):
    """Replace infinite or NaN values with 0 (or any valid number)."""
    sanitized = {}
    for key, value in sensor_data.items():
        if isinstance(value, float):
            if math.isinf(value) or math.isnan(value):
                sanitized[key] = 0
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value
    return sanitized

class ServerClient:
    def __init__(self, base_url):
        self.url = base_url.rstrip('/') + '/post_data'
        print(f"ServerClient initialized with URL: {self.url}")

        self.sio = socketio.Client()

        # Add connection event logging.
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)

        self.sio.connect(base_url)

    def on_connect(self):
        print("Raspi client connected to server via Socket.IO.")

    def on_disconnect(self):
        print("Raspi client disconnected from server.")

    def send_sensor_data(self, sensor_data):
        sensor_data = sanitize_data(sensor_data)
        self.sio.emit('sensor_data', sensor_data)
