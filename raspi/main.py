import csv
import time
from smbus2 import SMBus
from bicep_curl_detector import BicepCurlDetector
from FXAS21002C import FXAS21002C
from FXOS8700 import FXOS8700
from kalman_filter import OrientationFilter
from rep_data_processor import RepDataProcessor
from client import FirebaseClient
from clientserver import ServerClient
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


FXOS8700_ADDR = 0x1F
FXAS21002_ADDR = 0x21
FXOS8700_CTRL_REG1 = 0x2A
FXOS8700_OUT_X_MSB = 0x01
FXOS8700_M_OUT_X_MSB = 0x33
FXAS21002_CTRL_REG1 = 0x13
FXAS21002_OUT_X_MSB = 0x01


def main():
    # Initialize the server client with your server's base URL.
    server_client = ServerClient("http://172.20.10.4:5000/")

    with SMBus(1) as bus:
        fxos = FXOS8700(bus)
        fxas = FXAS21002C(bus)
        filter_ = OrientationFilter()

        # Calibrate sensors
        fxos.calibrate()
        fxas.calibrate()

        try:
            while True:
                ax, ay, az, mx, my, mz = fxos.read_accel_mag()
                gx, gy, gz = fxas.read_gyro()

                raw_pitch = filter_.update(gy, ax, ay, az)
                pitch = raw_pitch  # Pitch value to plot.

                sensor_data = {
                    "timestamp": time.time(),
                    "pitch": pitch
                }

                server_client.send_sensor_data(sensor_data)

                time.sleep(0.02)
        except KeyboardInterrupt:
            print("Terminated by user.")

if __name__ == "__main__":
    main()
