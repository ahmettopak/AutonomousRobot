# robot_controller.py
from receiver import UDPReceiver
from sender import UDPSender

class RobotController:
    def __init__(self, server_ip='127.0.0.1', server_port=5005):
        self.receiver = UDPReceiver(ip=server_ip, port=server_port)
        self.sender = UDPSender(server_ip=server_ip, server_port=server_port)

        # Set default on_message_received handler
        self.receiver.on_message_received = self.default_on_message_received

    def default_on_message_received(self, message, addr):
        """Default handler for incoming messages."""
        print(f"Default handler received message: {message} from {addr}")

    def start_server(self):
        """Start the UDP server."""
        self.receiver.start()

    def stop_server(self):
        """Stop the UDP server."""
        self.receiver.stop()

    def send_message(self, message):
        """Send a message to the server."""
        self.sender.send_message(message)

    def close(self):
        """Close the UDP client socket."""
        self.sender.close()
