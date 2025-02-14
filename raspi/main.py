import csv
import time
from smbus2 import SMBus
from bicep_curl_detector import BicepCurlDetector
from FXAS21002C import FXAS21002C
from FXOS8700 import FXOS8700
# from kalman_filter import OrientationFilter
from complementary_filter import OrientationFilter
from rep_data_processor import RepDataProcessor
from client import FirebaseClient
from clientserver import ServerClient


FXOS8700_ADDR = 0x1F
FXAS21002_ADDR = 0x21

FXOS8700_CTRL_REG1 = 0x2A
FXOS8700_OUT_X_MSB = 0x01
FXOS8700_M_OUT_X_MSB = 0x33

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

    server_client = ServerClient("http://172.20.10.4:5000")


    with SMBus(1) as bus:
        fxos = FXOS8700(bus)
        fxas = FXAS21002C(bus)
        filter_ = OrientationFilter()
        detector = BicepCurlDetector()
        aggregator = RepDataProcessor()

        # Calibrate sensors
        fxos.calibrate()
        fxas.calibrate()
        last_time = time.time() 
        last_rep_count = 0
        timout =  0
        try:
            while True:
                # Calculate dt
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                ax, ay, az, mx, my, mz = fxos.read_accel_mag()
                gx, gy, gz = fxas.read_gyro()


                start_time_uodate = time.time()
                raw_pitch = filter_.update(gy, ax, ay, az, dt=dt)
                end_time_update = time.time()
                pitch = raw_pitch  # Pitch value to plot. 
                rep_count = detector.detect_rep(pitch, gy)
                aggregator.update(pitch, gz, az)

                
                elapsed_update = (end_time_update - start_time_uodate) * 1000
                print(f"kalman calculation took {elapsed_update:.3f} ms")

                if pitch < 10:
                    timout += dt
                    if timout >= 5:
                        print("Timeout")
                        
                        sensor_data = {
                            "timestamp": time.time(),
                            "pitch": pitch,
                            "shoulder_movement": az,
                            "rep_count": rep_count,
                            "gyro": gz,
                            'end': 1,
                        }
                        server_client.send_sensor_data(sensor_data)
                        break
                else:
                    timout = 0

                sensor_data = {
                    "timestamp": time.time(),
                    "pitch": pitch,
                    "shoulder_movement": az,
                    "rep_count": rep_count,
                    "gyro": gz,
                }
                
                start_time_send = time.time()
                server_client.send_sensor_data(sensor_data)
                end_time_send = time.time()

                elapsed_send = (end_time_send - start_time_send) * 1000
                # print(f"Sending data took {elapsed_send:.3f} ms\n")

                time.sleep(0.02)
        except KeyboardInterrupt:
            print("Terminated by user.")

if __name__ == "__main__":
    main()

