import math
import asyncio

from gps_module import GPSModule, GPSType
from network_communication import NetworkCommunication
from imu_module import IMUModule
from web_socket_client import WebSocketClient

class RobotNavigation:
    max_speed = 100
    min_speed = -100

    autonomous_max_speed = 33
    autonomous_min_speed = -33
    autonomous_finish_tolerance = 0.01  

    def __init__(self, web_socket_client: WebSocketClient, gps_module: GPSModule, imu_module: IMUModule, network_communication: NetworkCommunication):
        self.web_socket_client = web_socket_client
        self.gps_module = gps_module
        self.imu_module = imu_module
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
        # Simple control strategy
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

    async def navigate_to_target(self, target_latitude, target_longitude):
        self.target_latitude = target_latitude
        self.target_longitude = target_longitude

        while True:
            current_latitude, current_longitude = self.gps_module.get_current_location()
            distance = self.haversine_distance(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            
            if distance < self.autonomous_finish_tolerance:
                print("Reached target!")
                await self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, 0))
                await self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, 0))
                break

            target_bearing = self.calculate_bearing(current_latitude, current_longitude, self.target_latitude, self.target_longitude)
            current_bearing = self.imu_module.get_heading()

            bearing_difference = target_bearing - current_bearing
            left_motor_speed, right_motor_speed = self.calculate_turn_speed(bearing_difference)

            # Constrain motor speeds
            left_motor_speed = max(self.autonomous_min_speed, min(self.autonomous_max_speed, left_motor_speed))
            right_motor_speed = max(self.autonomous_min_speed, min(self.autonomous_max_speed, right_motor_speed))

            #await self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, left_motor_speed))
            #await self.network_communication.send_byte_message(self.network_communication.command_maker.create_speed_command(self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, right_motor_speed))

            data_to_send = f"{current_latitude},{current_longitude},{current_bearing}"
            #await self.web_socket_client.send_data(data_to_send)
            print(f"Robot- Lat: {current_latitude}, Lon: {current_longitude}")


            await asyncio.sleep(0.1)  # Sleep for stability

    async def drive_by_speed(self, left_speed, right_speed):
        # Constrain motor speeds
        left_speed = max(self.min_speed, min(self.max_speed, left_speed))
        right_speed = max(self.min_speed, min(self.max_speed, right_speed))
        
        await self.network_communication.send_byte_message(
            self.network_communication.command_maker.create_speed_command(
                self.network_communication.command_maker.LEFT_MOTOR_SPEED_ID, left_speed))
        await self.network_communication.send_byte_message(
            self.network_communication.command_maker.create_speed_command(
                self.network_communication.command_maker.RIGHT_MOTOR_SPEED_ID, right_speed))

    async def drive_by_joystick(self, x, y):
        # Calculate motor speeds based on joystick data
        left_speed = y + x
        right_speed = y - x

        # Constrain motor speeds
        left_speed = max(self.min_speed, min(self.max_speed, left_speed))
        right_speed = max(self.min_speed, min(self.max_speed, right_speed))

        # Control motors
        await self.drive_by_speed(left_speed, right_speed)
