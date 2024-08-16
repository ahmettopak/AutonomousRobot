# receiver.py
import socket
import threading

class UDPReceiver:
    def __init__(self, ip='0.0.0.0', port=5005):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.on_message_received = None

    def start(self):
        """Start the UDP receiver to listen for incoming messages."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        self.is_running = True
        print(f"UDP receiver is listening on {self.ip}:{self.port}")

        def server_thread():
            while self.is_running:
                data, addr = self.server_socket.recvfrom(1024)  # Buffer size is 1024 bytes
                if self.on_message_received:
                    self.on_message_received(data.decode(), addr)
                response = "Message received"
                self.server_socket.sendto(response.encode(), addr)

        # Start server thread
        threading.Thread(target=server_thread, daemon=True).start()

    def stop(self):
        """Stop the UDP receiver."""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            print("UDP receiver stopped.")
