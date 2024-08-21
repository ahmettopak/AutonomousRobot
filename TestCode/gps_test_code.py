import serial
from enum import Enum, auto
from typing import Tuple, Optional

class GPSType(Enum):
    GARMIN = auto()
    RADIOLINK = auto()

SERIAL_PORT = '/dev/ttyUSB0'  # Bu portu gerçek cihazınıza göre ayarlayın

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
            GPSType.RADIOLINK: 9600
            # Diğer GPS modülleri için baud rate ayarları buraya eklenebilir
        }
        return baud_rates.get(gps_type, 115200)  # Varsayılan olarak 115200

    def _parse_gpgga(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:

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

    
        parts = sentence.split(',')
        if len(parts) < 8:
            return None, None
        try:
            latitude = parts[3]
            longitude = parts[5]
            lat_dir = parts[4]
            lon_dir = parts[6]

            if latitude and longitude:
                latitude = float(latitude)
                longitude = float(longitude)

                latitude = latitude / 100.0
                longitude = longitude / 100.0

                if lat_dir == 'S':
                    latitude = -latitude
                if lon_dir == 'W':
                    longitude = -longitude

                return latitude, longitude
            else:
                return None, None
        except ValueError:
            return None, None

    def _parse_gngga(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) < 7:
            return None, None
        try:
            latitude = parts[2]
            longitude = parts[4]
            lat_dir = parts[3]
            lon_dir = parts[5]

            if latitude and longitude:
                latitude = float(latitude)
                longitude = float(longitude)

                latitude = latitude / 100.0
                longitude = longitude / 100.0

                if lat_dir == 'S':
                    latitude = -latitude
                if lon_dir == 'W':
                    longitude = -longitude

                return latitude, longitude
            else:
                return None, None
        except ValueError:
            return None, None

    def _parse_gnrmc(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) < 8:
            return None, None
        try:
            latitude = parts[3]
            longitude = parts[5]
            lat_dir = parts[4]
            lon_dir = parts[6]

            if latitude and longitude:
                latitude = float(latitude)
                longitude = float(longitude)

                latitude = latitude / 100.0
                longitude = longitude / 100.0

                if lat_dir == 'S':
                    latitude = -latitude
                if lon_dir == 'W':
                    longitude = -longitude

                return latitude, longitude
            else:
                return None, None
        except ValueError:
            return None, None
  
    def _parse_gnvtg(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) < 5:
            return None, None
        try:
            course = parts[1]
            speed = parts[3]

            if course and speed:
                course = float(course) if course else None
                speed = float(speed) if speed else None
                return course, speed
            else:
                return None, None
        except ValueError:
            return None, None

    def _parse_gngsa(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) < 18:
            return None, None
        try:
            pdop = parts[15]
            hdop = parts[16]
            vdop = parts[17]

            pdop = float(pdop) if pdop else None
            hdop = float(hdop) if hdop else None
            vdop = float(vdop) if vdop else None

            return pdop, hdop
        except ValueError:
            return None, None

    def _parse_gpgsv(self, sentence: str) -> Tuple[Optional[int], Optional[int]]:
        parts = sentence.split(',')
        if len(parts) < 4:
            return None, None
        try:
            num_msgs = int(parts[1])
            msg_num = int(parts[2])
            satellites_in_view = int(parts[3])

            return num_msgs, satellites_in_view
        except ValueError:
            return None, None

    def _parse_glgsv(self, sentence: str) -> Tuple[Optional[int], Optional[int]]:
        parts = sentence.split(',')
        if len(parts) < 4:
            return None, None
        try:
            num_msgs = int(parts[1])
            msg_num = int(parts[2])
            satellites_in_view = int(parts[3])

            return num_msgs, satellites_in_view
        except ValueError:
            return None, None


    def _parse_gngll(self, sentence: str) -> Tuple[Optional[float], Optional[float]]:
        parts = sentence.split(',')
        if len(parts) < 6:
            return None, None
        try:
            latitude = parts[1]
            longitude = parts[3]
            lat_dir = parts[2]
            lon_dir = parts[4]

            if latitude and longitude:
                latitude = float(latitude)
                longitude = float(longitude)

                latitude = latitude / 100.0
                longitude = longitude / 100.0

                if lat_dir == 'S':
                    latitude = -latitude
                if lon_dir == 'W':
                    longitude = -longitude

                return latitude, longitude
            else:
                return None, None
        except ValueError:
            return None, None


        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if not line:
                    continue  # Skip empty lines

                latitude, longitude = None, None

                if line.startswith('$GNGGA'):
                    latitude, longitude = self._parse_gpgga(line)
                elif line.startswith('$GNGRMC'):
                    latitude, longitude = self._parse_gngrmc(line)
                elif line.startswith('$GNGLL'):
                    latitude, longitude = self._parse_gngll(line)
                else:
                    print(f"{self.gps_type} not parse data. Data: {line}")

                if latitude is not None and longitude is not None:
                    self.update_current_location(latitude, longitude)

    def read_gps_data(self):
        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if not line:
                    continue  # Skip empty lines

                latitude, longitude = None, None

                if line.startswith('$GNGGA'):
                    latitude, longitude = self._parse_gngga(line)
                elif line.startswith('$GNGRMC'):
                    latitude, longitude = self._parse_gnrmc(line)
                elif line.startswith('$GNVTG'):
                    latitude, longitude = self._parse_gnvtg(line)
                elif line.startswith('$GNGSA'):
                    latitude, longitude = self._parse_gngsa(line)
                elif line.startswith('$GPGSV'):
                    latitude, longitude = self._parse_gpgsv(line)
                elif line.startswith('$GLGSV'):
                    latitude, longitude = self._parse_glgsv(line)
                elif line.startswith('$GNGLL'):
                    latitude, longitude = self._parse_gngll(line)
                else:
                    print(f"{self.gps_type} not parse data. Data: {line}")

                if latitude is not None and longitude is not None:
                    self.update_current_location(latitude, longitude)


    def update_current_location(self, latitude: float, longitude: float):
        self.current_latitude = latitude
        self.current_longitude = longitude
        print(f"Updated Location -> Latitude: {self.current_latitude}, Longitude: {self.current_longitude}")

    def get_current_location(self) -> Tuple[float, float]:
        return self.current_latitude, self.current_longitude

# Örnek kullanım
if __name__ == "__main__":
    # GPS türünü belirleme
    gps_type = GPSType.GARMIN  # veya GPSType.ARADIOLINK

    # GPS modülünü oluşturma
    gps_module = GPSModule(gps_type)

    # GPS verilerini okuma (bu işlemi sürekli olarak yapacak)
    try:
        while True:
            gps_module.read_gps_data()
    except KeyboardInterrupt:
        print("GPS okuma durduruldu.")