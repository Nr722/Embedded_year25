import csv
import time
import math
from smbus2 import SMBus
from filterpy.kalman import KalmanFilter
import numpy as np

# Sensor Addresses (Ensure you have these defined)
FXOS8700_ADDR = 0x1F
FXAS21002_ADDR = 0x21
FXOS8700_CTRL_REG1 = 0x2A
FXOS8700_OUT_X_MSB = 0x01
FXOS8700_M_OUT_X_MSB = 0x33
FXAS21002_CTRL_REG1 = 0x13
FXAS21002_OUT_X_MSB = 0x01

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
