import threading
from gps_module import GPSModule , GPSType
from network_communication import NetworkCommunication
from robot_navigation import RobotNavigation
from imu_module import IMUModule
from web_socket_client import WebSocketClient
class RobotController:
    gps_type = GPSType.RADIOLINK  # veya GPSType.GARMIN

    uri = "ws://192.168.1.58:2006"
    

    def __init__(self):
        self.gps_module = GPSModule(gps_type=self.gps_type)
        self.imu_module = IMUModule()
        self.client = WebSocketClient(self.uri)
        
        # print("Heading:", imu.get_heading())
        # print("Speed:", imu.get_speed())
        self.network_communication = NetworkCommunication()
        self.robot_navigation = RobotNavigation(self.client , self.gps_module, self.imu_module , self.network_communication)
        self.gps_thread = threading.Thread(target=self.gps_module.read_gps_data, daemon=True)
        self.imu_thread = threading.Thread(target=self.imu_module.read_imu_data, daemon=True)

    def start(self):

        self.client.connect()
        self.network_communication.start_server()
        self.gps_thread.start()
        self.imu_thread.start()


    def stop(self):
        self.network_communication.stop_server()
        self.network_communication.close()

    def navigate(self ,target_latitude, target_longitude):
        self.robot_navigation.navigate_to_target(target_latitude, target_longitude)
        
    def drive_robot_by_joystick(self ,x, y):
        self.robot_navigation.drive_by_joystick(x, y)

    def drive_robot_by_speed(self ,left_motor_speed, right_motor_speed):
        self.robot_navigation.drive_by_speed(left_motor_speed, right_motor_speed)
        
