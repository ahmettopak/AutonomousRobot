import serial

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

class IMUModule:
    def __init__(self):
        self.heading = None
        self.speed = None

    def read_imu_data(self):
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    # Varsayalım ki veriler `heading,speed` formatında
                    try:
                        data = line.split(',')
                        if len(data) == 2:
                            self.heading = float(data[0])
                            self.speed = float(data[1])
                    except ValueError:
                        # Verinin doğru formatta olup olmadığını kontrol et
                        print("Hatalı veri formatı:", line)
    
    def get_heading(self):
        return self.heading

    def get_speed(self):
        return self.speed