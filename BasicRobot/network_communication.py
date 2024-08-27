import asyncio
from Base.receiver import UDPReceiver
from Base.sender import UDPSender
from Base.command_maker import RobotCommandMaker

class NetworkCommunication:
    def __init__(self, server_ip='192.168.3.2', server_port=10006):
        self.receiver = UDPReceiver(port=server_port)
        self.sender = UDPSender(server_ip=server_ip, server_port=server_port)
        self.command_maker = RobotCommandMaker()
        self.heartbeat_interval = 0.5
        self.heartbeat_task = None
        self.heartbeat_running = False

        self.receiver.on_message_received = self.default_on_message_received

    def default_on_message_received(self, message, addr):
        print(f"Default handler received message: {message} from {addr}")

    async def start_server(self):
        self.receiver.start()
        self.heartbeat_running = True
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())

    async def stop_server(self):
        self.receiver.stop()
        self.heartbeat_running = False
        if self.heartbeat_task is not None:
            await self.heartbeat_task

    def send_message(self, message):
        self.sender.send_message(message)

    def send_byte_message(self, message):
        self.sender.send_byte_message(message)

    async def send_heartbeat(self):
        while self.heartbeat_running:
            heartbeat_command = self.command_maker.create_heart_beat_command()
            self.send_byte_message(heartbeat_command)
            await asyncio.sleep(self.heartbeat_interval)  # Asenkron uyuma süresi

    async def close(self):
        self.sender.close()
