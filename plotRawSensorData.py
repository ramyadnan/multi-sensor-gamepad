import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'filteredSensorData/4filteredSensorData.csv'  # Adjust the path as necessary
data = pd.read_csv(file_path)

# Convert the Timestamp to a pandas datetime format for proper plotting
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Plot GSR vs Timestamp
plt.figure(figsize=(15, 6))
plt.plot(data['Timestamp'], data['GSR'], label='GSR', color='b')

# Adding labels and title
plt.xlabel('Timestamp')
plt.ylabel('GSR')
plt.title('GSR (Galvanic Skin Response) Readings Over Time')
plt.xticks(rotation=45)
plt.grid(True)

# Display the plot
plt.tight_layout()
plt.show()
