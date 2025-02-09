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


# def main():
#     firebase_client = FirebaseClient("https://eslabtest-eae29-default-rtdb.firebaseio.com/")

#     with SMBus(1) as bus:
#         fxos = FXOS8700(bus)
#         fxas = FXAS21002C(bus)
#         filter_ = OrientationFilter()
#         detector = BicepCurlDetector()
#         aggregator = RepDataProcessor()

#         # Perform calibration
#         fxos.calibrate()
#         fxas.calibrate()
#         count =1
#         last_rep_count = 0
#         try:
#             while True:

#                 ax, ay, az, mx, my, mz = fxos.read_accel_mag()
#                 gx, gy, gz = fxas.read_gyro()

#                 # Compute pitch
#                 raw_pitch = filter_.update(gy, ax, ay, az)
#                 pitch = raw_pitch  # No extra offset needed

#                 aggregator.update(pitch, gz, az)

#                 # Detect reps
#                 rep_count = detector.detect_rep(pitch, gy)
                
#                 if rep_count > last_rep_count:
                    
#                     count +=1
#                     rep_data = aggregator.get_aggregated_data()
#                     rep_data["rep_number"] = rep_count
#                     rep_data["timestamp"] = time.time()  # add timestamp if needed
                    
#                     firebase_client.send_rep_data(rep_data)
                    
#                     # Reset aggregator for the next rep.
#                     aggregator.reset()
#                     last_rep_count = rep_count
#                     print(f'im in here{rep_count}, {last_rep_count}, {count}')

#                 # Save data
#                 timestamp = time.time()
#                 time.sleep(0.015)  # Run at ~50Hz

#         except KeyboardInterrupt:
#             print('set done')


# if __name__ == "__main__":
#     main()



# import time
# from smbus2 import SMBus
# from FXAS21002C import FXAS21002C
# from FXOS8700 import FXOS8700
# from kalman_filter import OrientationFilter
# from clientserver import ServerClient

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
                # Read sensor data.
                ax, ay, az, mx, my, mz = fxos.read_accel_mag()
                gx, gy, gz = fxas.read_gyro()

                # Compute pitch using your orientation filter.
                raw_pitch = filter_.update(gy, ax, ay, az)
                pitch = raw_pitch  # Pitch value to plot.

                # Create a data packet with a timestamp and pitch.
                sensor_data = {
                    "timestamp": time.time(),
                    "pitch": pitch
                }

                # Send sensor data to the server immediately.
                server_client.send_sensor_data(sensor_data)

                # Maintain ~50Hz update rate (adjust as needed).
                time.sleep(0.02)
        except KeyboardInterrupt:
            print("Terminated by user.")

if __name__ == "__main__":
    main()
