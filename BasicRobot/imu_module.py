import serial

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

class IMUModule:
    def __init__(self):
        self.heading = 0
        self.speed = 0

    def read_imu_data(self):
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    try:
                        data = line.split(',')
                        if len(data) == 2:
                            self.heading = float(data[0])
                            self.speed = float(data[1])
                        
                            #print(f"Heading: {self.heading:.2f}°, Speed: {self.speed:.2f} m/s")
                    except ValueError:
                        print("Hatalı veri formatı:", line)
    
    def get_heading(self):
        return self.heading

    def get_speed(self):
        return self.speed
    