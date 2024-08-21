import threading
from gps_module import GPSModule
from network_communication import NetworkCommunication
from robot_navigation import RobotNavigation

class RobotController:
    def __init__(self):
        self.gps_module = GPSModule()
        self.network_communication = NetworkCommunication()
        self.robot_navigation = RobotNavigation(self.gps_module, self.network_communication)
        self.gps_thread = threading.Thread(target=self.gps_module.read_gps_data, daemon=True)

    def start(self):
        self.network_communication.start_server()
        self.gps_thread.start()

    def stop(self):
        self.network_communication.stop_server()
        self.network_communication.close()

    def navigate(self ,target_latitude, target_longitude):
        self.robot_navigation.navigate_to_target(target_latitude, target_longitude)
        
    def drive_robot_by_joystick(self ,x, y):
        self.robot_navigation.drive_by_joystick(x, y)

    def drive_robot_by_speed(self ,left_motor_speed, right_motor_speed):
        self.robot_navigation.drive_by_speed(left_motor_speed, right_motor_speed)
        
