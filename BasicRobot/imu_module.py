import serial

SERIAL_PORT = '/dev/sparkfun_9dof'
BAUD_RATE = 115200

class IMUModule:

    def read_imu_data(self):
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                print(line)

imu = IMUModule()
imu.read_imu_data()
