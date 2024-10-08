import threading
from gps_module import GPSModule , GPSType
from network_communication import NetworkCommunication
from robot_navigation import RobotNavigation
from imu_module import IMUModule
from web_socket_client import WebSocketClient

import time
class RobotController:
    gps_type = GPSType.RADIOLINK  

    uri = "ws://192.168.3.30:2006"
    
    robot_gps_id = "ROBOT_GPS"
    rcu_gps_id  = "RCU_GPS"
    rtl_start_time_id = "RTL_START_TIME"
    autonomous_stop_id = "AUTONOMOUS_STOP"

    rtl_start_time = 5
    

    rcu_latitude = 0.0
    rcu_longitude = 0.0

    heartbeat_received = False
    first_connection_flag = False
    navigate_started = False

    def __init__(self):
        self.gps_module = GPSModule(gps_type=self.gps_type)
        self.imu_module = IMUModule()
        self.client = WebSocketClient(self.uri)
        
        self.path = []  # Geçilen lokasyonları saklamak için liste
        self.last_latitude = None
        self.last_longitude = None
        self.recording_interval = 1  # Konum güncelleme aralığı (saniye cinsinden)
        self.distance_threshold = 3  # Mesafe eşiği (metre cinsinden)
        self.is_recording_path = False
        self.is_returning = False
        
        self.network_communication = NetworkCommunication()
        self.robot_navigation = RobotNavigation(self.client , self.gps_module, self.imu_module , self.network_communication)
        self.gps_thread = threading.Thread(target=self.gps_module.read_gps_data, daemon=True)
        self.imu_thread = threading.Thread(target=self.imu_module.read_imu_data, daemon=True)
        self.web_socket_send_thread = threading.Thread(target=self.send_gps_data2robot, daemon=True)
        self.web_socket_receive_thread = threading.Thread(target=self.receive_gps_data2robot, daemon=True)
        self.connection_check_thread = threading.Thread(target=self.check_connection, daemon=True)

    def start(self):
        self.client.connect()
        self.network_communication.start_server()
        self.gps_thread.start()
        self.imu_thread.start()
        self.web_socket_send_thread.start()
        self.web_socket_receive_thread.start()
        self.connection_check_thread.start()


    def stop(self):

        # Wait for threads to finish
        self.gps_thread.join()
        self.imu_thread.join()
        self.web_socket_send_thread.join()
        self.web_socket_receive_thread.join()
        self.connection_check_thread.join()

        # Stop network communication
        self.network_communication.stop_server()
        self.network_communication.close()
        
        # Disconnect WebSocket
        self.client.close()

    def send_gps_data2robot(self):
        while(True):
            current_latitude, current_longitude = self.gps_module.get_current_location()
            #current_latitude, current_longitude = 0,0

            if current_latitude is None or current_longitude is None:
                print("GPS verisi alınamadı. Bekleniyor...")
                time.sleep(1)  # GPS verisi gelene kadar bekle
                #continue
            
            data_to_send = f"{self.robot_gps_id},{current_latitude},{current_longitude},{self.imu_module.get_heading()}"

            self.client.send_data(data_to_send)

            time.sleep(2)

    def receive_gps_data2robot(self):

        while True:
            try:
                response = self.client.receive_data()

                # Check if response is None
                if response is None:
                    #print("No data received.")
                    time.sleep(0.1)
                    continue
                
                response_str = response.decode('utf-8')

                data_parts = response_str.split(',')
                
                # # Optional: Check if the expected number of parts is present
                # if len(data_parts) != 4:
                #     raise ValueError("Data parts length mismatch")
                
                id = data_parts[0]
              

                if id == self.rcu_gps_id:
                    latitude = float(data_parts[1])
                    longitude = float(data_parts[2])
                    heading = float(data_parts[3])
                    self.heartbeat_received = True
                    self.first_connection_flag = True
                    self.rcu_latitude = latitude
                    self.rcu_longitude = longitude

                    #self.stop_navigation()
                    print(f"{id} Latitude: {latitude}, Longitude: {longitude}")

                elif id == self.autonomous_stop_id:
                    self.stop_navigation()
                elif id == self.rtl_start_time_id:
                    self.rtl_start_time = int(data_parts[1])
                    
                else:
                    print("Unknown GPS ID!")

            except (IndexError, ValueError) as e:
                print(f"Error processing data: {e}")
                print(f"Response data: {response}")

            time.sleep(0.1)

    def check_connection(self):
        last_heartbeat_time = time.time()
        
        while True:
            current_time = time.time()

            if self.first_connection_flag:

                if not self.heartbeat_received:

                    if current_time - last_heartbeat_time >= self.rtl_start_time:
                        print("Heartbeat lost for 30 seconds. Starting home return process...")
                    

                        self.navigate(self.rcu_latitude , self.rcu_longitude)
#                        self.navigate(self.rcu_latitude , self.rcu_longitude)

                        self.navigate_to_home()
                else:
                    last_heartbeat_time = current_time
                    self.heartbeat_received = False
                
                time.sleep(1)  # Her saniye durumu kontrol et

    
    def navigate(self ,target_latitude, target_longitude):
        if not self.navigate_started:
            self.robot_navigation.navigate_status = True

            self.robot_navigation.navigate_to_target(target_latitude, target_longitude)
        else:
            print("Navigate already started!")
            

    def navigate_to_home(self):
        if not self.navigate_started:
            self.robot_navigation.navigate_status = True

            self.robot_navigation.follow_path(self.path.reverse())
        else:
            print("follow_path Navigate already started!")
            
    def stop_navigation(self):
        self.robot_navigation.navigate_status = False
        self.robot_navigation.stop_motors()
        


    def update_path(self):
        current_latitude, current_longitude = self.gps_module.get_current_location()

        if self.last_latitude is None or self.last_longitude is None:
            # İlk konum, yolu başlatma
            self.last_latitude = current_latitude
            self.last_longitude = current_longitude
            self.path.append((self.last_latitude, self.last_longitude))
            print(f"İlk konum kaydedildi: ({self.last_latitude}, {self.last_longitude})")
        else:
            distance = self.haversine_distance(self.last_latitude, self.last_longitude, current_latitude, current_longitude)
            if distance >= self.distance_threshold:
                self.path.append((current_latitude, current_longitude))
                print(f"Yeni konum kaydedildi: ({current_latitude}, {current_longitude})")
                self.last_latitude = current_latitude
                self.last_longitude = current_longitude
