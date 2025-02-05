#!/usr/bin/env python3

import time
import math
from smbus2 import SMBus
from filterpy.kalman import KalmanFilter
import numpy as np

# I2C Addresses for Your Sensors
FXOS8700_ADDR = 0x1F
FXAS21002_ADDR = 0x21

# FXOS8700 Registers (Accel + Mag)
FXOS8700_CTRL_REG1 = 0x2A
FXOS8700_OUT_X_MSB = 0x01
FXOS8700_M_OUT_X_MSB = 0x33

# FXAS21002 Registers (Gyro)
FXAS21002_CTRL_REG1 = 0x13
FXAS21002_OUT_X_MSB = 0x01


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
            # Detect peak (isometric contraction)
            if pitch > PITCH_PEAK_THRESHOLD and abs(gy) < 5:
                # print("Peak contraction detected")
                x=5
                
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

# FXOS8700 Accelerometer + Magnetometer
import csv
import time
import math
from smbus2 import SMBus
from filterpy.kalman import KalmanFilter
import numpy as np

# Sensor Addresses (Ensure you have these defined)
FXOS8700_ADDR = 0x1F  # Replace with actual address
FXAS21002_ADDR = 0x21  # Replace with actual address
FXOS8700_CTRL_REG1 = 0x2A
FXOS8700_OUT_X_MSB = 0x01
FXOS8700_M_OUT_X_MSB = 0x33
FXAS21002_CTRL_REG1 = 0x13
FXAS21002_OUT_X_MSB = 0x01

class FXOS8700:
    def __init__(self, bus):
        self.bus = bus
        self.initialize()
        self.accel_offset = [0, 0, 0]
        self.mag_offset = [0, 0, 0]

    def initialize(self):
        self.bus.write_byte_data(FXOS8700_ADDR, FXOS8700_CTRL_REG1, 0x00)  # Standby
        self.bus.write_byte_data(FXOS8700_ADDR, FXOS8700_CTRL_REG1, 0x01)  # Activate

    def calibrate(self, samples=100):
        """Calibrate accelerometer and magnetometer offsets."""
        print("Calibrating accelerometer and magnetometer...")

        accel_readings = np.zeros(3)
        mag_readings = np.zeros(3)

        for _ in range(samples):
            ax, ay, az, mx, my, mz = self.read_accel_mag(raw=True)
            accel_readings += np.array([ax, ay, az])
            mag_readings += np.array([mx, my, mz])
            time.sleep(0.01)  # Small delay

        self.accel_offset = (accel_readings / samples).tolist()
        self.mag_offset = (mag_readings / samples).tolist()

        print(f"Accelerometer offsets: {self.accel_offset}")
        print(f"Magnetometer offsets: {self.mag_offset}\n")

    def read_accel_mag(self, raw=False):
        accel_data = self.bus.read_i2c_block_data(FXOS8700_ADDR, FXOS8700_OUT_X_MSB, 6)
        mag_data = self.bus.read_i2c_block_data(FXOS8700_ADDR, FXOS8700_M_OUT_X_MSB, 6)

        sensitivity = 8192  # For ±2g mode (adjust if using ±4g or ±8g)
        ax = (self.twos_comp((accel_data[0] << 8) | accel_data[1], 14) >> 2) * 9.81 / sensitivity
        ay = (self.twos_comp((accel_data[2] << 8) | accel_data[3], 14) >> 2) * 9.81 / sensitivity
        az = (self.twos_comp((accel_data[4] << 8) | accel_data[5], 14) >> 2) * 9.81 / sensitivity

        mx = self.twos_comp((mag_data[0] << 8) | mag_data[1], 16)
        my = self.twos_comp((mag_data[2] << 8) | mag_data[3], 16)
        mz = self.twos_comp((mag_data[4] << 8) | mag_data[5], 16)

        if raw:
            return ax, ay, az, mx, my, mz

        return (
            ax - self.accel_offset[0],
            ay - self.accel_offset[1],
            az - self.accel_offset[2],
            mx - self.mag_offset[0],
            my - self.mag_offset[1],
            mz - self.mag_offset[2]
        )

    @staticmethod
    def twos_comp(val, bits):
        if val & (1 << (bits - 1)):
            val -= 1 << bits
        return val

class FXAS21002C:
    def __init__(self, bus):
        self.bus = bus
        self.initialize()
        self.gyro_offset = [0, 0, 0]

    def initialize(self):
        self.bus.write_byte_data(FXAS21002_ADDR, FXAS21002_CTRL_REG1, 0x00)  # Standby
        self.bus.write_byte_data(FXAS21002_ADDR, FXAS21002_CTRL_REG1, 0x0E)  # Set ODR and enable
        self.bus.write_byte_data(FXAS21002_ADDR, 0x0D, 0x03)  # Set full-scale range to ±250 dps

    def calibrate(self, samples=100):
        """Calibrate gyroscope offsets."""
        print("Calibrating gyroscope...")

        gyro_readings = np.zeros(3)

        for _ in range(samples):
            gx, gy, gz = self.read_gyro(raw=True)
            gyro_readings += np.array([gx, gy, gz])
            time.sleep(0.01)

        self.gyro_offset = (gyro_readings / samples).tolist()
        print(f"Gyroscope offsets: {self.gyro_offset}\n")

    def read_gyro(self, raw=False):
        gyro_data = self.bus.read_i2c_block_data(FXAS21002_ADDR, FXAS21002_OUT_X_MSB, 6)

        gx = self.twos_comp((gyro_data[0] << 8) | gyro_data[1], 16)
        gy = self.twos_comp((gyro_data[2] << 8) | gyro_data[3], 16)
        gz = self.twos_comp((gyro_data[4] << 8) | gyro_data[5], 16)

        sensitivity = 32768 / 250  # Adjust based on full-scale range
        gx, gy, gz = gx / sensitivity, gy / sensitivity, gz / sensitivity

        if raw:
            return gx, gy, gz

        return (
            gx - self.gyro_offset[0],
            gy - self.gyro_offset[1],
            gz - self.gyro_offset[2]
        )

    @staticmethod
    def twos_comp(val, bits):
        if val & (1 << (bits - 1)):
            val -= 1 << bits
        return val

def main():
    with SMBus(1) as bus:
        fxos = FXOS8700(bus)
        fxas = FXAS21002C(bus)
        filter_ = OrientationFilter()
        detector = BicepCurlDetector()

        # Perform calibration
        fxos.calibrate()
        fxas.calibrate()

        csv_filename = "bicep_curl_data.csv"
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "Pitch", "Reps"])

            try:
                while True:
                    ax, ay, az, mx, my, mz = fxos.read_accel_mag()
                    gx, gy, gz = fxas.read_gyro()

                    # Compute pitch
                    raw_pitch = filter_.update(gy, ax, ay, az)
                    pitch = raw_pitch  # No extra offset needed

                    # Detect reps
                    rep_count = detector.detect_rep(pitch, gy)

                    # Save data
                    timestamp = time.time()
                    writer.writerow([timestamp, ax, ay, az, gx, gy, gz, mx, my, mz, pitch, rep_count])
                    file.flush()
                    time.sleep(0.015)  # Run at ~50Hz

            except KeyboardInterrupt:
                print(f"Data saved to {csv_filename}. Exiting...")

if __name__ == "__main__":
    main()
