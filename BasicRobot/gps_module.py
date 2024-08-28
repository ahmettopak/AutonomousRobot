import serial
from enum import Enum, auto
from typing import Tuple, Optional
import pynmea2

class GPSType(Enum):
    GARMIN = auto()
    RADIOLINK = auto()
    UNKNOWN = auto()



SERIAL_PORT = '/dev/ttyUSB1'  # Bu portu gerçek cihazınıza göre ayarlayın

# GPS modülü sınıfı
class GPSModule:


    def __init__(self, gps_type: GPSType):
        self.current_latitude = 0.0
        self.current_longitude = 0.0
        self.gps_type = gps_type
        self.baud_rate = self._get_baud_rate_for_type(gps_type)
        self.serial_port = SERIAL_PORT  # Seri portu ayarlıyoruz

    def _get_baud_rate_for_type(self, gps_type: GPSType) -> int:
        # GPS modül türüne göre baud rate ayarları
        baud_rates = {
            GPSType.GARMIN: 115200,
            GPSType.RADIOLINK: 9600,
            GPSType.UNKNOWN: 9600

            # Diğer GPS modülleri için baud rate ayarları buraya eklenebilir
        }
        return baud_rates.get(gps_type, 115200)  # Varsayılan olarak 115200

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


    def _parse_gngrmc(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) < 8:
            return None, None
        try:
            latitude = float(parts[3])
            longitude = float(parts[5])
            lat_dir = parts[4]
            lon_dir = parts[6]

            latitude = latitude / 100.0
            longitude = longitude / 100.0

            if lat_dir == 'S':
                latitude = -latitude
            if lon_dir == 'W':
                longitude = -longitude

            return latitude, longitude
        except ValueError:
            print(f"Error parsing GNGRMC sentence: {sentence}")
            return None, None

    def parse_nmea_sentence(self, sentence: str):
        try:
            msg = pynmea2.parse(sentence)
            return msg
        except pynmea2.ParseError as e:
            #print(f"Parse error: {e}")
            return None

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
    
    
    def handle_parsed_message(self, msg):
        if isinstance(msg, pynmea2.RMC):
            timestamp = getattr(msg, 'timestamp', 'N/A')
            lat = getattr(msg, 'lat', 'N/A')
            lon = getattr(msg, 'lon', 'N/A')
            status = getattr(msg, 'status', 'N/A')
            print(f"RMC - Time: {timestamp}, Lat: {lat}, Lon: {lon}, Status: {status}")

        elif isinstance(msg, pynmea2.GGA):
            timestamp = getattr(msg, 'timestamp', 'N/A')
            lat = getattr(msg, 'lat', 'N/A')
            lon = getattr(msg, 'lon', 'N/A')
            altitude = getattr(msg, 'altitude', 'N/A')
            altitude_units = getattr(msg, 'altitude_units', 'N/A')
            print(f"GGA - Time: {timestamp}, Lat: {lat}, Lon: {lon}, Altitude: {altitude} {altitude_units}")

        elif isinstance(msg, pynmea2.VTG):
            true_course = getattr(msg, 'true_course', 'N/A')
            magnetic_course = getattr(msg, 'magnetic_course', 'N/A')
            speed_kph = getattr(msg, 'speed_kph', 'N/A')
            speed_knots = getattr(msg, 'speed_knots', 'N/A')
            print(f"VTG - True Course: {true_course}, Magnetic Course: {magnetic_course}, Speed: {speed_kph} km/h, Speed: {speed_knots} knots")

        elif isinstance(msg, pynmea2.GSA):
            mode = getattr(msg, 'mode', 'N/A')
            fix_type = getattr(msg, 'fix_type', 'N/A')
            print(f"GSA - Mode: {mode}, Fix Type: {fix_type}")

        elif isinstance(msg, pynmea2.GSV):
            num_messages = getattr(msg, 'num_messages', 'N/A')
            message_number = getattr(msg, 'message_number', 'N/A')
            num_sats_in_view = getattr(msg, 'num_sats_in_view', 'N/A')
            print(f"GSV - Number of Messages: {num_messages}, Message Number: {message_number}, Number of Satellites: {num_sats_in_view}")
            # Iterate through satellite details if available
            for sat in getattr(msg, 'sats', []):
                prn = getattr(sat, 'prn', 'N/A')
                elevation = getattr(sat, 'elevation', 'N/A')
                azimuth = getattr(sat, 'azimuth', 'N/A')
                snr = getattr(sat, 'snr', 'N/A')
                print(f"Satellite: PRN: {prn}, Elevation: {elevation}, Azimuth: {azimuth}, SNR: {snr}")

        elif isinstance(msg, pynmea2.GLL):
            lat = getattr(msg, 'lat', 'N/A')
            lon = getattr(msg, 'lon', 'N/A')
            status = getattr(msg, 'status', 'N/A')
            print(f"GLL - Lat: {lat}, Lon: {lon}, Status: {status}")

        elif isinstance(msg, pynmea2.GNS):
            mode = getattr(msg, 'mode', 'N/A')
            num_sats = getattr(msg, 'num_sats', 'N/A')
            print(f"GNS - Mode: {mode}, Num Satellites: {num_sats}")

        elif isinstance(msg, pynmea2.GST):
            rms_error = getattr(msg, 'rms_error', 'N/A')
            print(f"GST - RMS Error: {rms_error}")

        else:
            print(f"Unhandled message type: {msg}")

    def read_gps_data(self):
        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
            latitude, longitude = None, None
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()

                if self.gps_type == GPSType.GARMIN:
                    latitude, longitude = self._parse_gpgga(line)
                elif self.gps_type == GPSType.RADIOLINK:
                    parsed_msg = self.parse_nmea_sentence(line)
                    if False:
                        self.handle_parsed_message(parsed_msg)
                    else:
                        # Special handling for unsupported sentences
                        if line.startswith('$GNGGA'):
                            lat, lon = self.manual_parse_gga(line)
                            #print(f"Manual GGA - Lat: {lat}, Lon: {lon}")
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
        print(f"Updated Location -> Latitude: {self.current_latitude}, Longitude: {self.current_longitude}")

    def get_current_location(self) -> Tuple[float, float]:
        return self.current_latitude, self.current_longitude