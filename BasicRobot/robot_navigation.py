import math
import time

from gps_module import GPSModule, GPSType
from network_communication import NetworkCommunication
from imu_module import IMUModule
from web_socket_client import WebSocketClient

class RobotNavigation:
    navigate_status = False
    max_speed = 100
    min_speed = -100

    autonomous_max_speed = 33
    autonomous_min_speed = -33

    autonomous_turn_max_speed = 15
    autonomous_turn_min_speed = -15

    autonomous_turn_offset = 25

    autonomous_finish_tolerance = 0.005

    def __init__(self, web_socket_client: WebSocketClient, gps_module: GPSModule, imu_module: IMUModule, network_communication: NetworkCommunication):
        self.web_socket_client = web_socket_client
        self.gps_module = gps_module
        self.imu_module = imu_module
        self.network_communication = network_communication
        self.target_latitude = None
        self.target_longitude = None

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0  # Dünya'nın yarıçapı, kilometre cinsinden
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        dlon = math.radians(lon2 - lon1)
        y = math.sin(dlon) * math.cos(math.radians(lat2))
        x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon)
        bearing = math.degrees(math.atan2(y, x))
        bearing = (bearing + 360) % 360
        return bearing

    def calculate_turn_speed(self, bearing_difference):

        if bearing_difference > self.autonomous_turn_offset:
            left_motor_speed =  self.autonomous_turn_max_speed
            right_motor_speed = self.autonomous_turn_min_speed
        elif bearing_difference < -self.autonomous_turn_offset:
            left_motor_speed =  self.autonomous_turn_min_speed
            right_motor_speed = self.autonomous_turn_max_speed
        else:
            left_motor_speed = self.autonomous_max_speed
            right_motor_speed = self.autonomous_max_speed
        return left_motor_speed, right_motor_speed
    
    def stop_motors(self):
        self.drive_by_speed(0,0)

    def navigate_to_target(self, target_latitude, target_longitude):
        self.target_latitude = target_latitude
        self.target_longitude = target_longitude

        while self.navigate_status:
            current_latitude, current_longitude = self.gps_module.get_current_location()
 
            if current_latitude is None or current_longitude is None:
                print("GPS verisi alınamadı. Bekleniyor...")
                time.sleep(1)  # GPS verisi gelene kadar bekle
                continue

            distance = self.haversine_distance(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            
            if distance < self.autonomous_finish_tolerance:
                print("Hedefe ulaşıldı!")
                self.stop_motors()
                break

            target_bearing = self.calculate_bearing(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            current_bearing = self.imu_module.get_heading()

            if current_bearing is None:
                print("IMU verisi alınamadı. Bekleniyor...")
                time.sleep(1)  # IMU verisi gelene kadar bekle
                continue

            bearing_difference = target_bearing - current_bearing
            left_motor_speed, right_motor_speed = self.calculate_turn_speed(bearing_difference)

            self.drive_by_speed(left_motor_speed , right_motor_speed)

            print(f"Robot Navigation - \n Current Lat: {current_latitude}, Lon: {current_longitude}, Bearing: {current_bearing}\n Target Lat: {target_latitude} , Lon: {target_longitude} , Bearing: {target_bearing}, \n Bearing Difference: {bearing_difference} , Distance: {distance}")

            time.sleep(0.1)  # Stabilite için kısa bir uyuma süresi

    def follow_path(self , path):
        while self.navigate_status:
            target_latitude, target_longitude = self.path.pop(0)
            while True:
                current_latitude, current_longitude = self.gps_module.get_current_location()
                
                if current_latitude is None or current_longitude is None:
                    print("GPS verisi alınamadı. Bekleniyor...")
                    time.sleep(1)  # GPS verisi gelene kadar bekle
                    continue

                distance = self.haversine_distance(current_latitude, current_longitude, target_latitude, target_longitude)
                
                if distance < self.autonomous_finish_tolerance:
                    print(f"Bir sonraki hedefe ulaşıldı! ({target_latitude}, {target_longitude})")
                    self.stop_motors()
                    break

                target_bearing = self.calculate_bearing(current_latitude, current_longitude, target_latitude, target_longitude)
                current_bearing = self.imu_module.get_heading()

                if current_bearing is None:
                    print("IMU verisi alınamadı. Bekleniyor...")
                    time.sleep(1)  # IMU verisi gelene kadar bekle
                    continue

                bearing_difference = target_bearing - current_bearing
                left_motor_speed, right_motor_speed = self.calculate_turn_speed(bearing_difference)

                self.drive_by_speed(left_motor_speed, right_motor_speed)

                print(f"Robot Navigation - \n Current Lat: {current_latitude}, Lon: {current_longitude}, Bearing: {current_bearing}\n Target Lat: {target_latitude}, Lon: {target_longitude}, Bearing: {target_bearing}, \n Bearing Difference: {bearing_difference}, Distance: {distance}")

                time.sleep(0.1)  # Stabilite için kısa bir uyuma süresi

        self.is_returning = False
        print("Geri dönüş tamamlandı.")

    def drive_by_speed(self, left_speed, right_speed):
        # Motor hızlarını sınırlandır
        left_speed = max(self.min_speed, min(self.max_speed, left_speed))
        right_speed = max(self.min_speed, min(self.max_speed, right_speed))
        
        self.network_communication.send_byte_message(
            self.network_communication.command_maker.create_speed_command(
                self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, left_speed))
                    
        time.sleep(0.10)

        self.network_communication.send_byte_message(
            self.network_communication.command_maker.create_speed_command(
                self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, right_speed))
