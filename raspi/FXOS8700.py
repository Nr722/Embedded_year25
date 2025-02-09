import time
import math
from smbus2 import SMBus
from filterpy.kalman import KalmanFilter
import numpy as np


FXOS8700_ADDR = 0x1F
FXAS21002_ADDR = 0x21
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
