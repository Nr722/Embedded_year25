import time
import math
import smbus2
import csv

# I2C addresses
FXOS8700_ADDR = 0x1f
FXAS21002_ADDR = 0x21

# I2C bus
bus = smbus2.SMBus(1)

# FXOS8700 Registers
FXOS8700_CTRL_REG1 = 0x2A
FXOS8700_OUT_X_MSB = 0x01

# FXAS21002 Registers
FXAS21002_CTRL_REG1 = 0x13
FXAS21002_OUT_X_MSB = 0x01

# Initialize Sensors
def init_fxos8700():
    bus.write_byte_data(FXOS8700_ADDR, FXOS8700_CTRL_REG1, 0x01)

def init_fxas21002():
    bus.write_byte_data(FXAS21002_ADDR, FXAS21002_CTRL_REG1, 0x0E)

def read_sensor_data(address, reg, length=6):
    data = bus.read_i2c_block_data(address, reg, length)
    x = (data[0] << 8) | data[1]
    y = (data[2] << 8) | data[3]
    z = (data[4] << 8) | data[5]
    if x & 0x8000: x -= 65536
    if y & 0x8000: y -= 65536
    if z & 0x8000: z -= 65536
    return x, y, z

def get_accel_data():
    ax_raw, ay_raw, az_raw = read_sensor_data(FXOS8700_ADDR, FXOS8700_OUT_X_MSB, length=6)
    ax = ax_raw / 4096.0
    ay = ay_raw / 4096.0
    az = az_raw / 4096.0
    return ax, ay, az

def get_gyro_data():
    gx_raw, gy_raw, gz_raw = read_sensor_data(FXAS21002_ADDR, FXAS21002_OUT_X_MSB, length=6)
    gx = gx_raw / 16.0
    gy = gy_raw / 16.0
    gz = gz_raw / 16.0
    return gx, gy, gz

def vector_magnitude(x, y, z):
    return math.sqrt(x*x + y*y + z*z)

def get_accel_angle(ax, ay, az):
    return math.atan2(ay, math.sqrt(ax**2 + az**2)) * (180.0 / math.pi)

# Initialize sensors
init_fxos8700()
init_fxas21002()

# State Machine: 4 States
WAITING_FOR_START = 0
UP_PHASE = 1
WAITING_FOR_DOWN = 2
DOWN_PHASE = 3
state = WAITING_FOR_START

# Thresholds for detecting movement
start_threshold = 7
top_threshold = 10  
end_threshold = 5  
gyro_start_threshold = 20.0 
gyro_end_threshold = 10.0  
min_start_count = 2
min_top_count = 2  
min_wait_for_down_count = 3
min_end_count = 5  

start_count = 0
top_count = 0
wait_for_down_count = 0
end_count = 0
rep_count = 0
rep_data = []
max_angle = -float('inf')  # Track peak angle
up_end_time = None  # Track when up phase ends

# CSV file setup
raw_file = open("raw_data.csv", "w", newline="")
feature_file = open("bicep_curl_metrics.csv", "w", newline="")

raw_writer = csv.writer(raw_file)
feature_writer = csv.writer(feature_file)

# Write headers
raw_writer.writerow(["Time", "Accel_X", "Accel_Y", "Accel_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Accel_Mag", "Gyro_Mag"])
feature_writer.writerow(["Rep", "Up Duration (s)", "Down Duration (s)", "ROM (degrees)", "Max Accel Mag (g)", 
                         "Max Gyro Mag (dps)", "Min Gyro Mag (dps)", "Avg Accel Mag (g)", "Avg Gyro Mag (dps)", 
                         "Peak Up Velocity (dps)", "Peak Down Velocity (dps)", "Jerk (smoothness)"])

print("Starting bicep curl monitoring. Press Ctrl+C to stop...")

try:
    while True:
        current_time = time.time()

        # Read sensors
        ax, ay, az = get_accel_data()
        gx, gy, gz = get_gyro_data()

        # Compute magnitudes
        accel_mag = vector_magnitude(ax, ay, az)
        gyro_mag = vector_magnitude(gx, gy, gz)

        # Calculate range of motion using accel angles
        accel_angle = get_accel_angle(ax, ay, az)

        # Store raw data
        raw_writer.writerow([current_time, ax, ay, az, gx, gy, gz, accel_mag, gyro_mag])

        if state == WAITING_FOR_START:
            if accel_mag > start_threshold or gyro_mag > gyro_start_threshold:
                print(f'accel_mag: {accel_mag}, gyro_mag: {gyro_mag}')
                start_count += 1
            else:
                start_count = 0

            if start_count >= min_start_count:
                state = UP_PHASE
                rep_start_time = current_time
                rep_data = []
                rep_count += 1
                max_angle = accel_angle  # Reset max angle
                print(f"\n*** Rep {rep_count} START (Up Phase) ***\n")

        elif state == UP_PHASE:
            rep_data.append((current_time, accel_mag, gyro_mag, accel_angle))

            # Track the highest point reached
            if accel_angle > max_angle:
                max_angle = accel_angle
                up_end_time = current_time  # Store time at peak

            # Wait until there is minimal motion for a short time (indicating a pause)
            if accel_mag < top_threshold and gyro_mag < gyro_end_threshold:
                top_count += 1
                if top_count >= min_top_count:
                    state = WAITING_FOR_DOWN
                    print(f"*** Pause detected at top, waiting for downward motion ***")
                    print(f'gyro_x: {gx}, gyro_y: {gy}, gyro_z: {gz}')
            else:
                top_count = 0  # Reset if movement resumes

        elif state == WAITING_FOR_DOWN:
            # Detect downward movement after the pause
            if accel_mag > start_threshold or gyro_mag > gyro_start_threshold:
                wait_for_down_count += 1
                # print(f'Waiting for down count: {wait_for_down_count}')
            else:
                wait_for_down_count = 0

            if wait_for_down_count >= min_wait_for_down_count:
                state = DOWN_PHASE
                print('accel_mag: ', accel_mag, 'gyro_mag: ', gyro_mag)
                print(f"*** Transitioning to DOWN PHASE ***")

        elif state == DOWN_PHASE:
            rep_data.append((current_time, accel_mag, gyro_mag, accel_angle))
            
            if accel_mag < end_threshold and gyro_mag < gyro_end_threshold:
                end_count += 1
            else:
                end_count = 0

            if end_count >= min_end_count:
                state = WAITING_FOR_START
                rep_end_time = current_time

                # Ensure up_end_time is valid
                if up_end_time is None:
                    up_end_time = rep_start_time  # Default to start time

                # Compute Features
                up_duration = up_end_time - rep_start_time
                down_duration = rep_end_time - up_end_time

                max_accel_mag = max(x[1] for x in rep_data)
                max_gyro_mag = max(x[2] for x in rep_data)
                min_gyro_mag = min(x[2] for x in rep_data)
                avg_accel_mag = sum(x[1] for x in rep_data) / len(rep_data)
                avg_gyro_mag = sum(x[2] for x in rep_data) / len(rep_data)

                # Compute ROM
                min_angle = min(x[3] for x in rep_data)
                ROM = max_angle - min_angle

                # Save features
                feature_writer.writerow([rep_count, up_duration, down_duration, ROM, max_accel_mag, max_gyro_mag, 
                                         min_gyro_mag, avg_accel_mag, avg_gyro_mag, max_gyro_mag, min_gyro_mag])

                print(f"\n*** Rep {rep_count} END ***\n")

                # Reset counters
                start_count = 0
                top_count = 0
                end_count = 0
                wait_for_down_count = 0  

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nStopping...")
    raw_file.close()
    feature_file.close()
