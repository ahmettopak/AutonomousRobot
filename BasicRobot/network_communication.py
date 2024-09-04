from Base.receiver import UDPReceiver
from Base.sender import UDPSender
from Base.command_maker import RobotCommandMaker

import time 
import threading


class NetworkCommunication:
    def __init__(self, server_ip='192.168.3.2', server_port=10006):
        self.receiver = UDPReceiver(port=server_port)
        self.sender = UDPSender(server_ip=server_ip, server_port=server_port)
        self.command_maker = RobotCommandMaker()
        self.heartbeat_interval = 0.5
        self.heartbeat_thread = None
        self.heartbeat_running = False

        self.receiver.on_message_received = self.default_on_message_received

    def default_on_message_received(self, message, addr):
        print(f"Default handler received message: {message} from {addr}")

    def start_server(self):
        #self.receiver.start()
        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        self.heartbeat_thread.start()

    def stop_server(self):
        self.receiver.stop()
        self.heartbeat_running = False
        if self.heartbeat_thread is not None:
            self.heartbeat_thread.join()

    def send_message(self, message):
        self.sender.send_message(message)

    def send_byte_message(self, message):
        self.sender.send_byte_message(message)

    def send_heartbeat(self):
        while self.heartbeat_running:
            heartbeat_command = self.command_maker.create_heart_beat_command()
            self.send_byte_message(heartbeat_command)
            time.sleep(self.heartbeat_interval)

    def close(self):
        self.sender.close()
