# This script filters the sensor data based on the timestamp range of matching joystick events 
# and creates a new CSV file containing only the sensor data within that timeframe.

import pandas as pd
import os
from datetime import datetime

def filter_sensor_data(sensor_file, joystick_file, output_file):

    joystick_data = pd.read_csv(joystick_file)
    sensor_data = pd.read_csv(sensor_file)

    joystick_data['Timestamp'] = pd.to_datetime(joystick_data['Timestamp'])
    sensor_data['Timestamp'] = pd.to_datetime(sensor_data['Timestamp'])

    joystick_start_time = joystick_data['Timestamp'].iloc[0]  # First event timestamp
    joystick_end_time = joystick_data['Timestamp'].iloc[-1]   # Last event timestamp

    filtered_sensor_data = sensor_data[(sensor_data['Timestamp'] >= joystick_start_time) & 
                                       (sensor_data['Timestamp'] <= joystick_end_time)]


    filtered_sensor_data.to_csv(output_file, index=False)

    print(f"Filtered sensor data saved to {output_file}")

# Loop to handle multiple files
for i in range(1, 11): 
    sensor_file = f"sensorData/{i}.sensorData.csv"
    joystick_file = f"controller_logging/logs/{i}.logData.csv"
    output_file = f"filteredSensorData/{i}filteredSensorData.csv"

    if os.path.exists(sensor_file) and os.path.exists(joystick_file):
        filter_sensor_data(sensor_file, joystick_file, output_file)
    else:
        print(f"Files for index {i} are missing. Skipping.")
