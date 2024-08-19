import serial
import math
import re

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

def parse_gpgga(sentence):
    parts = sentence.split(',')
    if len(parts) < 7:
        return None, None
    try:
        latitude = float(parts[2])
        longitude = float(parts[4])
        lat_dir = parts[3]
        lon_dir = parts[5]

        latitude = latitude / 100.0
        longitude = longitude / 100.0

        if lat_dir == 'S':
            latitude = -latitude
        if lon_dir == 'W':
            longitude = -longitude

        return latitude, longitude
    except ValueError:
        return None, None

class GPSModule:
    def __init__(self):
        self.current_latitude = 0.0
        self.current_longitude = 0.0

    def read_gps_data(self):
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$GPGGA'):
                    latitude, longitude = parse_gpgga(line)
                    if latitude is not None and longitude is not None:
                        self.update_current_location(latitude, longitude)

    def update_current_location(self, latitude, longitude):
        self.current_latitude = latitude
        self.current_longitude = longitude
        print(f"Updated Location -> Latitude: {self.current_latitude}, Longitude: {self.current_longitude}")

    def get_current_location(self):
        return self.current_latitude, self.current_longitude
