import threading
from gps_module import GPSModule , GPSType
from network_communication import NetworkCommunication
from robot_navigation import RobotNavigation
from imu_module import IMUModule
from web_socket_client import WebSocketClient

import time
class RobotController:
    gps_type = GPSType.RADIOLINK  # veya GPSType.GARMIN

    uri = "ws://192.168.3.58:2006"
    
    robot_gps_id = "ROBOT"
    rcu_gps_id  = "RCU"

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
        self.web_socket_send_thread = threading.Thread(target=self.send_gps_data2robot, daemon=True)
        self.web_socket_receive_thread = threading.Thread(target=self.receive_gps_data2robot, daemon=True)

    def start(self):
        self.client.connect()
        self.network_communication.start_server()
        self.gps_thread.start()
        self.imu_thread.start()
        self.web_socket_send_thread.start()
        self.web_socket_receive_thread.start()


    def stop(self):

        # Wait for threads to finish
        self.gps_thread.join()
        self.imu_thread.join()
        self.web_socket_send_thread.join()
        self.web_socket_receive_thread.join()
        
        # Stop network communication
        self.network_communication.stop_server()
        self.network_communication.close()
        
        # Disconnect WebSocket
        self.client.close()

    def send_gps_data2robot(self):
        while(True):
            current_latitude, current_longitude = self.gps_module.get_current_location()

            data_to_send = f"{self.robot_gps_id},{current_latitude},{current_longitude},{self.imu_module.get_heading()}"

            self.client.send_data(data_to_send)

            time.sleep(1)

    def receive_gps_data2robot(self):
        while True:
             
            try:
                response = self.client.receive_data()
                response_str = response.decode('utf-8')
                data_parts = response_str.split(',')
                
                # if len(data_parts) != 3:
                #     raise ValueError("Data parts length mismatch")
                
                id = data_parts[0]
                latitude = float(data_parts[1])
                longitude = float(data_parts[2])
                heading = float(data_parts[3])
                
                print(f"{id} Latitude: {latitude}, Longitude: {longitude}, Heading: {heading}")
            except (IndexError, ValueError) as e:
                print(f"Error processing data: {e}")
                print(f"Response data: {response}")

                time.sleep(0.1)

    def navigate(self ,target_latitude, target_longitude):
        self.robot_navigation.navigate_to_target(target_latitude, target_longitude)
        
    def stop_navigation(self ,target_latitude, target_longitude):
        self.robot_navigation.stop_navigation()
        
    def drive_robot_by_joystick(self ,x, y):
        self.robot_navigation.drive_by_joystick(x, y)

    def drive_robot_by_speed(self ,left_motor_speed, right_motor_speed):
        self.robot_navigation.drive_by_speed(left_motor_speed, right_motor_speed)
        
