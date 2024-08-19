# sender.py
import socket

import Base.command_maker as command_maker
class UDPSender:
    def __init__(self, server_ip='127.0.0.1', server_port=5005):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, message):
        """Send a message to the UDP server."""
        self.client_socket.sendto(message.encode(), (self.server_ip, self.server_port))
        print(f"Sent message: {message} to {self.server_ip}:{self.server_port}")

        # Optionally, receive response
        try:
            data, addr = self.client_socket.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received response: {data.decode()} from {addr}")
        except socket.timeout:
            print("No response received within the timeout period.")

    def send_byte_message(self, message_bytes):
        """Send a message to the UDP server."""
        if not isinstance(message_bytes, bytes):
            raise ValueError("Message must be a bytes object")
        
        self.client_socket.sendto(message_bytes, (self.server_ip, self.server_port))
        print(f"Sent byte message: {command_maker.RobotCommandMaker.get_message_with_dashes(message_bytes)} to {self.server_ip}:{self.server_port}")


    def close(self):
        """Close the UDP client socket."""
        self.client_socket.close()
        print("Client socket closed.")
