from receiver import UDPReceiver
from sender import UDPSender
from command_maker import RobotCommandMaker
import threading
import time

class RobotController:
    def __init__(self, server_ip='192.168.3.2', server_port=10006):
        self.receiver = UDPReceiver(port=server_port)
        self.sender = UDPSender(server_ip=server_ip, server_port=server_port)
        self.command_maker = RobotCommandMaker()
        self.heartbeat_interval = 0.02
        self.heartbeat_thread = None
        self.heartbeat_running = False

        self.receiver.on_message_received = self.default_on_message_received

    def default_on_message_received(self, message, addr):
        print(f"Default handler received message: {message} from {addr}")

    def start_server(self):
        self.receiver.start()
        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat)
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

    def drive_robot(self, left_speed, right_speed):
        left_speed = int(round(left_speed))
        right_speed = int(round(right_speed))

        left_speed_command = self.command_maker.create_speed_command(RobotCommandMaker.LEFT_MOTOR_SPEED_ID, left_speed)
        right_speed_command = self.command_maker.create_speed_command(RobotCommandMaker.RIGHT_MOTOR_SPEED_ID, right_speed)

        self.send_byte_message(left_speed_command)
        self.send_byte_message(right_speed_command)

    def send_heartbeat(self):
        while self.heartbeat_running:
            heartbeat_command = self.command_maker.create_heart_beat_command()
            self.send_byte_message(heartbeat_command)
            time.sleep(self.heartbeat_interval)

    def close(self):
        self.sender.close()


def main():
    # Initialize the RobotController
    controller = RobotController()

    try:
        # Start the server and heartbeat
        controller.start_server()

        # Example: Drive the robot
        controller.drive_robot(100, 100)
        time.sleep(5)  # Let the robot drive for 5 seconds

        # Stop the robot and server
        controller.drive_robot(0, 0)
        time.sleep(1)  # Ensure the stop command is processed
    finally:
        # Clean up resources
        controller.stop_server()
        controller.close()

if __name__ == "__main__":
    main()
