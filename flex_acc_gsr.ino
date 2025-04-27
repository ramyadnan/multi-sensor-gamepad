#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

const int flexLeftPin = A1;
const int flexRightPin = A2;
const int gsrPin = A0;

// Variables
int valueL, valueR, gsrValue;
const int sampleRate = 100;
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  // MPU6050 initialization
  Serial.println("Initializing MPU6050...");
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) delay(10);
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("Setup complete\n");
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastSampleTime >= sampleRate) {
    lastSampleTime = currentTime;

    // Read flex sensor values
    valueL = analogRead(flexLeftPin);
    valueR = analogRead(flexRightPin);

    // Read GSR sensor values
    long sum = 0;
    for (int i = 0; i < 10; i++) {
      sum += analogRead(gsrPin);
    }
    gsrValue = sum / 10;

    // Read MPU6050 values
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Print all sensor data
    Serial.print(valueL);
    Serial.print(",");
    Serial.print(valueR);
    Serial.print(",");
    Serial.print(gsrValue);
    Serial.print(",");
    Serial.print(a.acceleration.x);
    Serial.print(",");
    Serial.print(a.acceleration.y);
    Serial.print(",");
    Serial.print(a.acceleration.z);
    Serial.print(",");
    Serial.print(g.gyro.x);
    Serial.print(",");
    Serial.print(g.gyro.y);
    Serial.print(",");
    Serial.print(g.gyro.z);
    Serial.print(",");
    Serial.println(temp.temperature);
  }
}
