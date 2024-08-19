import math
import time 

class RobotNavigation:
    max_speed = 33
    min_speed = -33

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

    def navigate_to_target(self ,target_latitude, target_longitude):
        self.target_latitude =target_latitude
        self.target_longitude = target_longitude
        while True:

            current_latitude, current_longitude = self.gps_module.get_current_location()
            distance = self.haversine_distance(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            if distance < 0.01:
                print("Hedefe ulaşıldı!")
                self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, 0))
                self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, 0))
                break

            bearing = self.calculate_bearing(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            left_motor_speed = self.max_speed - bearing
            right_motor_speed = self.max_speed + bearing

            left_motor_speed = max(self.min_speed, min(self.max_speed, left_motor_speed))
            right_motor_speed = max(self.min_speed, min(self.max_speed, right_motor_speed))

            self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, left_motor_speed))
            self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, right_motor_speed))
            
            time.sleep(0.1)  # Increased sleep interval for stability

    def basic_navigate_to_target(self):
        while True:
            current_latitude, current_longitude = self.gps_module.get_current_location()
            distance = self.haversine_distance(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            if distance < 0.01:
                print("Hedefe ulaşıldı!")
                self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, 0))
                self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, 0))
                break

            bearing = self.calculate_bearing(current_latitude, current_longitude, self.target_latitude, self.target_longitude)

            if bearing > 10:
                left_motor_speed = 50
                right_motor_speed = -50
            elif bearing < -10:
                left_motor_speed = -50
                right_motor_speed = 50
            else:
                left_motor_speed = 100
                right_motor_speed = 100

            self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, left_motor_speed))
            self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, right_motor_speed))

            time.sleep(0.1)  # Increased sleep interval for stability
