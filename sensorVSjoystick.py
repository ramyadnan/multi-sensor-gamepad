# This script processes filtered sensor data by resampling it to 1-second intervals, 
# calculates the magnitudes of acceleration and gyroscope data, and compares it against 
# gamepad event counts by plotting both datasets over time. 
# It also averages sensor readings per second and visualizes the data in plots for each sensor, 
# displaying it alongside gamepad event activity per second. The plots are saved as PNG images for each sensor.


import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
from matplotlib.ticker import MaxNLocator

def process_sensor_data(sensor_files):
    """Processes sensor data, resampling it to 1-second intervals."""
    sensor_df_list = []

    for file in sensor_files:
        df = pd.read_csv(file, parse_dates=["Timestamp"])
        df["Time(s)"] = (df["Timestamp"] - df["Timestamp"].min()).dt.total_seconds()
        df = df.sort_values("Time(s)")
        sensor_df_list.append(df)

    sensor_df_combined = pd.concat(sensor_df_list)
    sensor_df_combined["Timedelta"] = pd.to_timedelta(sensor_df_combined["Time(s)"], unit="s")
    sensor_df_combined.set_index("Timedelta", inplace=True)
    
    sensor_df_resampled = sensor_df_combined.resample("1s").mean()
    
    # Compute acceleration and gyroscope magnitudes
    sensor_df_resampled["Accel_Magnitude"] = np.sqrt(sensor_df_resampled["Accel X"]**2 +
                                                       sensor_df_resampled["Accel Y"]**2 +
                                                       sensor_df_resampled["Accel Z"]**2)
    sensor_df_resampled["Gyro_Magnitude"] = np.sqrt(sensor_df_resampled["Gyro X"]**2 +
                                                      sensor_df_resampled["Gyro Y"]**2 +
                                                      sensor_df_resampled["Gyro Z"]**2)

    print("Total sensor time: ", sensor_df_combined["Time(s)"].max())
    return sensor_df_resampled

def process_gamepad_data(gamepad_files):
    """Processes gamepad data and converts timestamps to elapsed time in seconds."""
    gamepad_df_list = []

    for file in gamepad_files:
        df = pd.read_csv(file, parse_dates=["Timestamp"])
        df["Time(s)"] = (df["Timestamp"] - df["Timestamp"].min()).dt.total_seconds()
        df = df.sort_values("Time(s)")
        gamepad_df_list.append(df)

    gamepad_df_combined = pd.concat(gamepad_df_list)
    gamepad_df_combined["Timedelta"] = pd.to_timedelta(gamepad_df_combined["Time(s)"], unit="s")
    gamepad_df_combined.set_index("Timedelta", inplace=True)

    # Count gamepad events per second
    gamepad_df_resampled = gamepad_df_combined.resample("1s").count()
    gamepad_df_resampled.rename(columns={"JoystickID": "Event_Count"}, inplace=True)
    
    print("Total gamepad events time: ", gamepad_df_combined["Time(s)"].max())
    return gamepad_df_resampled

# Load sensor and gamepad data
sensor_files = glob.glob("filteredSensorData/*filteredSensorData.csv")
gamepad_files = glob.glob("filteredSensorData/*.logData.csv")

sensor_df = process_sensor_data(sensor_files)
gamepad_df = process_gamepad_data(gamepad_files)

# Merge sensor data and gamepad data (keeping all sensor timestamps)
merged_df = sensor_df.copy()
merged_df["Event_Count"] = gamepad_df["Event_Count"]

# List of sensors to plot (excluding temperature)
sensors = ["Left Sensor", "Right Sensor", "GSR", "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Accel_Magnitude", "Gyro_Magnitude"]

for sensor in sensors:
    fig, ax1 = plt.subplots(figsize=(15, 6))

    ax1.set_xlabel("Time(s)")
    ax1.set_ylabel(sensor, color="blue")
    ax1.plot(merged_df.index.total_seconds(), merged_df[sensor], label=sensor, color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Gamepad Event Count", color="green")
    ax2.plot(merged_df.index.total_seconds(), merged_df["Event_Count"], label="Gamepad Events", color="green", alpha=0.5)
    ax2.tick_params(axis='y', labelcolor="green")

    plt.title(f"{sensor} vs. Gamepad Events Over Time")
    plt.grid(True)
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig.tight_layout()

    # Collect all lines and labels from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    # Merge both legends and place them together
    ax1.legend(lines + lines2, labels + labels2, loc="upper left", fontsize=10)

    # Save plot as an image
    filename = f"Plotted/1-{sensor.replace(' ', '_')}_vs_Gamepad.png"
    plt.savefig(filename)
    plt.close()

    print(f"Saved: {filename}")
