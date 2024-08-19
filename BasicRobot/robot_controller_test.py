from receiver import UDPReceiver
from sender import UDPSender
from command_maker import RobotCommandMaker  # RobotCommandMaker sınıfını ekliyoruz

import threading
import time

class RobotController:
    def __init__(self, server_ip='192.168.3.2', server_port=10006):
        self.receiver = UDPReceiver(port=server_port)
        self.sender = UDPSender(server_ip=server_ip, server_port=server_port)
        self.command_maker = RobotCommandMaker()  # Create an instance of RobotCommandMaker
        self.heartbeat_interval = 0.02  # 20ms interval
        self.heartbeat_thread = None
        self.heartbeat_running = False

        # Set default on_message_received handler
        self.receiver.on_message_received = self.default_on_message_received

    def default_on_message_received(self, message, addr):
        """Default handler for incoming messages."""
        print(f"Default handler received message: {message} from {addr}")

    def start_server(self):
        """Start the UDP server and heartbeat thread."""
        self.receiver.start()
        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat)
        self.heartbeat_thread.start()

    def stop_server(self):
        """Stop the UDP server and heartbeat thread."""
        self.receiver.stop()
        self.heartbeat_running = False
        if self.heartbeat_thread is not None:
            self.heartbeat_thread.join()

    def send_message(self, message):
        """Send a message to the server."""
        self.sender.send_message(message)

    def send_byte_message(self, message):
        """Send a byte message to the server."""
        self.sender.send_byte_message(message)

    def drive_robot(self, left_speed, right_speed):
        """
        Create and send a drive command packet.

        :param left_speed: 1 byte left motor speed (0-255)
        :param right_speed: 1 byte right motor speed (0-255)
        """

        left_speed = int(round(left_speed))
        right_speed = int(round(right_speed))

        # Create a drive command using RobotCommandMaker
        left_speed_command = self.command_maker.create_speed_command(RobotCommandMaker.LEFT_MOTOR_SPEED_ID, left_speed)
        right_speed_command = self.command_maker.create_speed_command(RobotCommandMaker.RIGHT_MOTOR_SPEED_ID, right_speed)

        # Send the command
        self.send_byte_message(left_speed_command)
        self.send_byte_message(right_speed_command)

    def send_heartbeat(self):
        """Send heartbeat messages at regular intervals."""
        while self.heartbeat_running:
            hearbeat_command = self.command_maker.create_heart_beat_command()
            self.send_byte_message(hearbeat_command)
            time.sleep(self.heartbeat_interval)

    def close(self):
        """Close the UDP client socket."""
        self.sender.close()
