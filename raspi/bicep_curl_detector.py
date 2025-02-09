import time
import math
from smbus2 import SMBus
from filterpy.kalman import KalmanFilter
import numpy as np


# Thresholds for Rep Detection
PITCH_START_THRESHOLD = 20    # Start position (near 0°)
PITCH_PEAK_THRESHOLD = 90     # Peak position (~90° for full contraction)
GYRO_THRESHOLD = 20           # Movement detection threshold (deg/sec)
TIME_BETWEEN_REPS = 1       # Min time between reps (seconds)
# Class for Bicep Curl Detection
class BicepCurlDetector:
    def __init__(self):
        self.rep_count = 0
        self.in_rep = False
        self.last_rep_time = time.time()
    
    def detect_rep(self, pitch, gy):
        """
        Detects a full rep based on pitch angle and angular velocity.
        """
        current_time = time.time()
        
        if not self.in_rep:
            # Detect upward motion (concentric phase)
            if pitch < PITCH_START_THRESHOLD and gy > GYRO_THRESHOLD:
            # if gy > GYRO_THRESHOLD:
                print()
                self.in_rep = True
                # print("Rep started (lifting)")

        elif self.in_rep:

            # not using this rn
            # Detect peak (isometric contraction)
            # if pitch > PITCH_PEAK_THRESHOLD and abs(gy) < 5:
            #     # print("Peak contraction detected")
            #     x=5
                
            # Detect downward motion (eccentric phase)
            if pitch < PITCH_START_THRESHOLD and gy < -GYRO_THRESHOLD:
            # if pitch < PITCH_START_THRESHOLD:
            # if gy < -GYRO_THRESHOLD:
                if current_time - self.last_rep_time > TIME_BETWEEN_REPS:
                    self.rep_count += 1
                    self.last_rep_time = current_time
                    self.in_rep = False
                    print(f"Rep completed! Total reps: {self.rep_count}")

        return self.rep_count
