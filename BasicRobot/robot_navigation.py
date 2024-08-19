import math
import time

class RobotNavigation:
    max_speed = 33
    min_speed = -33
    tolerance = 0.01  # Mesafe toleransı

    def __init__(self, gps_module, network_communication):
        self.gps_module = gps_module
        self.network_communication = network_communication
        self.target_latitude = 39.47566589
        self.target_longitude = 32.4113875

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
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
        # Basit bir kontrol stratejisi
        # Bu hesaplamalar, hedefe yönelirken robotun dönüş hızlarını belirler.
        if bearing_difference > 10:
            left_motor_speed = 20
            right_motor_speed = -20
        elif bearing_difference < -10:
            left_motor_speed = -20
            right_motor_speed = 20
        else:
            left_motor_speed = 20
            right_motor_speed = 20
        return left_motor_speed, right_motor_speed

    def navigate_to_target(self, target_latitude, target_longitude):
        self.target_latitude = target_latitude
        self.target_longitude = target_longitude

        while True:
            current_latitude, current_longitude = self.gps_module.get_current_location()
            distance = self.haversine_distance(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            
            if distance < self.tolerance:
                print("Hedefe ulaşıldı!")
                self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, 0))
                self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, 0))
                break

            target_bearing = self.calculate_bearing(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            current_bearing = self.calculate_bearing(current_latitude, current_longitude, current_latitude, current_longitude)  # Bu örnek, mevcut yönü hesaplamak için bir yer tutucudur.

            bearing_difference = target_bearing - current_bearing
            left_motor_speed, right_motor_speed = self.calculate_turn_speed(bearing_difference)

            # Motor hızlarını sınırlandır
            left_motor_speed = max(self.min_speed, min(self.max_speed, left_motor_speed))
            right_motor_speed = max(self.min_speed, min(self.max_speed, right_motor_speed))

            self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, left_motor_speed))
            self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, right_motor_speed))

            time.sleep(0.1)  # Stabilite için uyuma süresi
