class RobotCommandMaker:

    R = 0x43
    C = 0x52
    
    DIR_POSITIVE = 0x01
    DIR_NEGATIVE = 0x00

    LEFT_MOTOR_SPEED_ID = 0xA4
    RIGHT_MOTOR_SPEED_ID = 0x84

    def __init__(self):
        pass

    def calculate_checksum(self, data_id, data0, data1):
        """Calculate checksum based on data_id, data0, and data1."""
        return (data_id + data0 + data1) % 256

    def create_command(self, data_id, data0, data1):
        """
        Create a 6-byte command packet.

        :param data_id: 1 byte data ID (0-255)
        :param data0: 1 byte data0 (0-255)
        :param data1: 1 byte data1 (0-255)
        :return: bytes object representing the command packet
        """
        if not all(0 <= x <= 255 for x in [data_id, data0, data1]):
            raise ValueError("All values must be in the range 0-255")

        # Calculate checksum
        cs = self.calculate_checksum(data_id, data0, data1)
        
        # Create the packet
        packet = bytearray([
            self.C,
            self.R,
            data_id,
            data0,
            data1,
            cs
        ])
        
        return bytes(packet)

    def create_speed_command(self, motor_id, speed):
        """
        Create a drive command packet.

        :param motor_id: 1 byte motor ID (0-255)
        :param speed: 1 byte speed (0-255)
        :return: bytes object representing the drive command packet
        """
        if speed >= 0:
            data0 = self.DIR_POSITIVE
        else:
            data0 = self.DIR_NEGATIVE
        
        data1 = abs(speed)

        return self.create_command(motor_id, data0, data1)

    def create_heart_beat_command(self):
        """
        Create a heartbeat command packet.

        :return: bytes object representing the heartbeat command packet
        """
        return self.create_command(0x41, 0x48, 0x4D)

    def parse_command(self, command):
        """
        Parse a 6-byte command packet.

        :param command: bytes object representing the command packet
        :return: tuple (sender_id, receiver_id, data_id, data0, data1, checksum)
        """
        if len(command) != 6:
            raise ValueError("Command must be exactly 6 bytes long")

        sender_id, receiver_id, data_id, data0, data1, checksum = command

        # Validate checksum
        expected_checksum = self.calculate_checksum(data_id, data0, data1)
        if checksum != expected_checksum:
            raise ValueError("Checksum does not match")

        return (sender_id, receiver_id, data_id, data0, data1, checksum)
    
    def get_message_with_dashes(message_bytes):
        """Print each byte in message_bytes separated by dashes."""
        # Convert bytes to a list of hex strings
        hex_strings = [f"{byte:02X}" for byte in message_bytes]
        # Join hex strings with dashes
        message_str = "-".join(hex_strings)
        return message_str