"""
This script interfaces with an Arduino via serial to collect sensor data in real-time and log it to CSV files.
Key features:
- Reads sensor data (e.g., Left Sensor, GSR, Acceleration, Gyroscope, Temperature) from Arduino.
- Timestamps each data entry and writes it to a new CSV file.
- Uses keyboard input to control logging:
  - 's' starts logging and creates a new file.
  - 'e' stops logging and closes the file.
  - 'q' exits the program and terminates the serial connection.
- Handles graceful termination with file closure and serial disconnection.
"""


import serial
import csv
import time
import threading
import os
from pynput import keyboard
from datetime import datetime 

arduino_port = '/dev/cu.usbserial-1410'
baud_rate = 115200

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
except serial.SerialException:
    print("Error: Could not open serial port. Check if it's connected!")
    exit()

logging = False
file = None
writer = None
running = True

# find the next available filename
def get_next_filename():
    index = 1
    while True:
        filename = f"/Users/nurramizahadnan/Python/gamepad/sensorData/sensorData{index}.csv"
        if not os.path.exists(filename):
            return filename
        index += 1

# Function to handle key presses
def on_press(key):
    global logging, file, writer, running

    try:
        if key.char == 's':  # Start logging
            if not logging:
                logging = True
                filename = get_next_filename()
                print(f"Logging started: {filename}")

                file = open(filename, mode='w', newline='')  # Open new file in write mode
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Left Sensor", "Right Sensor", "GSR", 
                                 "Accel X", "Accel Y", "Accel Z", 
                                 "Gyro X", "Gyro Y", "Gyro Z", "Temperature (C)"])
        
        elif key.char == 'e':  # Stop logging
            if logging:
                logging = False
                print("Logging stopped.")
                file.close()
        
        elif key.char == 'q':  # Quit program
            print("Exiting program...")
            running = False  # Stop the loop
            if logging:
                file.close()
            ser.close()  # close the serial connection
            return False  # Stop listener

    except AttributeError:
        pass  # Ignore special keys

# Run key listener in a separate thread
listener = keyboard.Listener(on_press=on_press)
listener.start()

try:
    while running:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()

            if logging:
                # Get the current timestamp (date, time, and ms)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + str(int(time.time() * 1000) % 1000).zfill(3)

                # Add the timestamp as the first element in the data to write into the CSV
                row = [timestamp] + data.split(',')
                print(row)  # You can print the row to debug and verify the timestamp

                # Write the row with timestamp to the CSV file
                writer.writerow(row)
                file.flush()  # Ensure data is saved

        time.sleep(0.1)

except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Exiting gracefully...")
    running = False
    if logging:
        file.close()
    ser.close()
