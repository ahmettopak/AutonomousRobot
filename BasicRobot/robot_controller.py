import asyncio
from gps_module import GPSModule, GPSType
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
        self.network_communication = NetworkCommunication()
        self.robot_navigation = RobotNavigation(self.client, self.gps_module, self.imu_module, self.network_communication)

    async def start(self):
        await self.client.connect()
        await self.network_communication.start_server()

        # Verileri sürekli okumak için asenkron görevler başlatma
        self.gps_task = asyncio.create_task(self._read_gps_data())
        self.imu_task = asyncio.create_task(self._read_imu_data())

    async def stop(self):
        await self.network_communication.stop_server()
        await self.network_communication.close()
        
        # Görevleri iptal etme ve bekleme
        self.gps_task.cancel()
        self.imu_task.cancel()
        try:
            await self.gps_task
        except asyncio.CancelledError:
            pass
        try:
            await self.imu_task
        except asyncio.CancelledError:
            pass

    async def _read_gps_data(self):    
        await self.gps_module.read_gps_data()
        
    async def _read_imu_data(self): 
        await self.imu_module.read_imu_data()

    async def navigate(self, target_latitude, target_longitude):
        await self.robot_navigation.navigate_to_target(target_latitude, target_longitude)

    async def drive_robot_by_joystick(self, x, y):
        await self.robot_navigation.drive_by_joystick(x, y)

    async def drive_robot_by_speed(self, left_motor_speed, right_motor_speed):
        await self.robot_navigation.drive_by_speed(left_motor_speed, right_motor_speed)
