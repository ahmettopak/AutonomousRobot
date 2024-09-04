import serial
from enum import Enum, auto
from typing import Tuple, Optional

class GPSType(Enum):
    GARMIN = auto()
    RADIOLINK = auto()
    UNKNOWN = auto()


SERIAL_PORT = '/dev/ttyUSB1'

class GPSModule:


    def __init__(self, gps_type: GPSType):
        self.current_latitude = 0.0
        self.current_longitude = 0.0
        self.gps_type = gps_type
        self.baud_rate = self._get_baud_rate_for_type(gps_type)
        self.serial_port = SERIAL_PORT 

    def _get_baud_rate_for_type(self, gps_type: GPSType) -> int:
        baud_rates = {
            GPSType.GARMIN: 115200,
            GPSType.RADIOLINK: 9600,
            GPSType.UNKNOWN: 9600

        }
        return baud_rates.get(gps_type, 115200) 
    

    def _parse_gpgga(self , sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        
        if len(parts) < 7:
            return None, None
        
        try:
            # Parse latitude and longitude values from the sentence
            lat_str = parts[2]
            lon_str = parts[4]
            lat_dir = parts[3]
            lon_dir = parts[5]

            # Convert latitude and longitude to float and correct them
            latitude = float(lat_str[:2]) + float(lat_str[2:]) / 60.0
            longitude = float(lon_str[:3]) + float(lon_str[3:]) / 60.0

            # Adjust latitude and longitude based on their direction
            if lat_dir == 'S':
                latitude = -latitude
            if lon_dir == 'W':
                longitude = -longitude

            return latitude, longitude
        except ValueError:
            return None, None

    def manual_parse_gga(self , sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) >= 6:
            try:
                lat = float(parts[2])
                lat_dir = parts[3]
                lon = float(parts[4])
                lon_dir = parts[5]

                # Convert latitude
                lat_deg = int(lat / 100)
                lat_min = lat % 100
                latitude = lat_deg + (lat_min / 60)
                if lat_dir == 'S':
                    latitude = -latitude

                # Convert longitude
                lon_deg = int(lon / 100)
                lon_min = lon % 100
                longitude = lon_deg + (lon_min / 60)
                if lon_dir == 'W':
                    longitude = -longitude

                return latitude, longitude
            except ValueError as e:
                #print(f"Value error: {e}")
                return None, None
        return None, None

    def read_gps_data(self):
        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
            latitude, longitude = None, None
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()

                if self.gps_type == GPSType.GARMIN:
                    latitude, longitude = self._parse_gpgga(line)
                elif self.gps_type == GPSType.RADIOLINK:
                    # Special handling for unsupported sentences
                    if line.startswith('$GNGGA'):
                        lat, lon = self.manual_parse_gga(line)
                        # print(f"Manual GGA - Lat: {lat}, Lon: {lon}")
                        self.update_current_location(lat, lon)

                    else:
                         #   print(f"Unhandled sentence: {line}")
                        pass
                else:
                    print(f"{self.gps_type} not parse data. Data: {line}")
                    continue
                
                if latitude is not None and longitude is not None:
                    self.update_current_location(latitude, longitude)

    def update_current_location(self, latitude: float, longitude: float):
        self.current_latitude = latitude
        self.current_longitude = longitude
       # print(f"Updated Location -> Latitude: {self.current_latitude}, Longitude: {self.current_longitude}")

    def get_current_location(self) -> Tuple[float, float]:
        return self.current_latitude, self.current_longitude