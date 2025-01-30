import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("raw_data.csv")

# Convert Time column to datetime (modify if time is in another format)
df["Time"] = pd.to_datetime(df["Time"], unit='s')  # Change 'unit' if needed

# Set Time as index for time series plotting
df.set_index("Time", inplace=True)

# Plot Acceleration Data
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Accel_X"], label="Accel_X")
plt.plot(df.index, df["Accel_Y"], label="Accel_Y")
plt.plot(df.index, df["Accel_Z"], label="Accel_Z")
plt.plot(df.index, df["Accel_Mag"], label="Accel_Mag", linestyle="dashed")

plt.title("Acceleration Time Series")
plt.xlabel("Time")
plt.ylabel("Acceleration (m/s²)")
plt.legend()
plt.grid()
plt.show()

# Plot Gyroscope Data
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Gyro_X"], label="Gyro_X")
plt.plot(df.index, df["Gyro_Y"], label="Gyro_Y")
plt.plot(df.index, df["Gyro_Z"], label="Gyro_Z")
plt.plot(df.index, df["Gyro_Mag"], label="Gyro_Mag", linestyle="dashed")

plt.title("Gyroscope Time Series")
plt.xlabel("Time")
plt.ylabel("Gyroscope (°/s)")
plt.legend()
plt.grid()
plt.show()
