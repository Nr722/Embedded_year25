import csv
import time
from smbus2 import SMBus
from bicep_curl_detector import BicepCurlDetector
from FXAS21002C import FXAS21002C
from FXOS8700 import FXOS8700
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


def flush_offline_buffer(server_client, offline_buffer):
    """
    Try to send all buffered aggregated rep data.
    If sending fails, leave the remaining data in the buffer.
    """
    i = 0
    while i < len(offline_buffer):
        try:
            server_client.send_sensor_data(offline_buffer[i])
            offline_buffer.pop(i)
        except Exception as e:
            break


def main():
    server_client = ServerClient("http://172.20.10.4:5000")
    offline_buffer = []

    with SMBus(1) as bus:
        fxos = FXOS8700(bus)
        fxas = FXAS21002C(bus)
        filter_ = OrientationFilter()
        detector = BicepCurlDetector()
        aggregator = RepDataProcessor()

        fxos.calibrate()
        fxas.calibrate()
        last_time = time.time() 
        last_rep_count = 0
        timeout = 0

        try:
            while True:

                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                
                ax, ay, az, mx, my, mz = fxos.read_accel_mag()
                gx, gy, gz = fxas.read_gyro()

                
                raw_pitch = filter_.update(gy, ax, ay, az, dt=dt)
                pitch = raw_pitch  
                rep_count = detector.detect_rep(pitch, gy)
                aggregator.update(pitch, gz, az)

                if rep_count > last_rep_count:
                    aggregated_data = aggregator.get_aggregated_data()
                    aggregated_data["timestamp"] = time.time()
                    aggregated_data["rep_count"] = rep_count

                    try:
                        server_client.send_sensor_data(aggregated_data)
                        flush_offline_buffer(server_client, offline_buffer)
                    except Exception as e:
                        print("Connection lost. Storing aggregated rep data offline.")
                        offline_buffer.append(aggregated_data)

                    last_rep_count = rep_count
                    aggregator.reset()

                if pitch < 10:
                    timeout += dt
                    if timeout >= 5:
                        print("Timeout reached. Finalizing rep data.")
                        aggregated_data = aggregator.get_aggregated_data()
                        aggregated_data["timestamp"] = time.time()
                        aggregated_data["end"] = 1  # Indicate end of exercise

                        try:
                            server_client.send_sensor_data(aggregated_data)
                            flush_offline_buffer(server_client, offline_buffer)
                        except Exception as e:
                            print("Connection lost during finalization. Storing data offline.")
                            offline_buffer.append(aggregated_data)
                        break
                else:
                    timeout = 0

                sensor_data = {
                    "timestamp": time.time(),
                    "pitch": pitch,
                    "shoulder_movement": az,
                    "rep_count": rep_count,
                    "gyro": gz,
                }
                try:
                    server_client.send_sensor_data(sensor_data)
                    flush_offline_buffer(server_client, offline_buffer)
                except Exception as e:
                    print("Connection error sending continuous data.")

                time.sleep(0.02)
        except KeyboardInterrupt:
            print("Terminated by user.")

        if offline_buffer:
            print("Attempting to flush offline aggregated data before exit...")
            flush_offline_buffer(server_client, offline_buffer)


if __name__ == "__main__":
    main()
