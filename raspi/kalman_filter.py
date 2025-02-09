import math
from smbus2 import SMBus
from filterpy.kalman import KalmanFilter
import numpy as np

# Kalman Filter for Pitch Estimation
class OrientationFilter:
    def __init__(self):
        """
        Initializes an adaptive Kalman filter for pitch estimation.
        Dynamically adjusts noise parameters based on movement speed.
        """
        self.use_kalman = True
            # Set to True to enable Kalman filter
        self.kf = KalmanFilter(dim_x=2, dim_z=1)
        self.kf.x = np.array([[0.0], [0.0]])  # Initial state: [pitch, pitch_rate]
        self.kf.F = np.array([[1, 0.02], [0, 1]])  # State transition matrix
        self.kf.H = np.array([[1, 0]])  # Measurement function
        self.kf.P *= 1e3  # Initial covariance matrix

        # Default noise values
        self.base_Q = np.array([[1e-2, 0], [0, 1e-2]])  # Process noise (default for slow movement)
        self.base_R = np.array([[5]])  # Measurement noise (default for accelerometer)

        self.kf.Q = self.base_Q
        self.kf.R = self.base_R

    def update(self, gyro_y, accel_x, accel_y, accel_z, dt=0.02):
        """
        Updates the pitch estimate using an adaptive Kalman filter.
        Adjusts noise levels dynamically based on movement speed.
        """
        # Compute pitch from accelerometer (based on gravity direction)
        accel_pitch = math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)) * (180.0 / math.pi)

        if not self.use_kalman:
            return accel_pitch  # Return raw pitch if Kalman filter is disabled

        # Estimate speed using gyroscope (higher speed → more trust in gyro)
        speed = abs(gyro_y)  # Use absolute gyro reading as a speed estimate

        # Dynamically adjust process noise (Q) and measurement noise (R)
        if speed > 100:  # High-speed movement
            self.kf.Q = self.base_Q * 10  # Increase process noise to adapt quickly
            self.kf.R = self.base_R * 0.5  # Reduce accelerometer noise impact
        elif speed > 50:  # Medium-speed movement
            self.kf.Q = self.base_Q * 5
            self.kf.R = self.base_R * 0.7
        else:  # Slow movement
            self.kf.Q = self.base_Q
            self.kf.R = self.base_R

        # Predict and update Kalman filter
        self.kf.predict()
        self.kf.update(np.array([[accel_pitch]]))

        return self.kf.x[0, 0]  # Estimated pitch
